"""Headless HR service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments (docs/04-architecture/a2ui-strategy.md). Responses
go through `_mask_profile` which honors the column-level
`info={"privacy": ...}` metadata declared in `hr.model`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.events import (
    HR_MEMBER_OFFBOARDED,
    HR_MEMBER_ONBOARDED,
    HR_PROFILE_UPDATED,
    emit_event,
)
from ..core.permissions import (
    PermissionDenied,
    is_workspace_admin,
    require_workspace_admin,
    require_workspace_member,
)
from ..core.shared import AuditDomain, AuditLog, RoleName
from .model import (
    PRIVACY_HR_ONLY,
    PRIVACY_MANAGER,
    PRIVACY_PUBLIC,
    PRIVACY_SELF_ONLY,
    EmployeeProfile,
    TenureStatus,
)
from .schemas import (
    EmployeeProfileCreateInput,
    EmployeeProfileListFilter,
    EmployeeProfileListOutput,
    EmployeeProfileOutput,
    EmployeeProfileUpdateInput,
    TenureTransitionInput,
)

# State machine (docs/02-product/domain-hr.md "EmployeeProfile 라이프사이클")
_VALID_TENURE_TRANSITIONS: dict[TenureStatus, set[TenureStatus]] = {
    TenureStatus.CANDIDATE: {TenureStatus.PRE_HIRE, TenureStatus.ARCHIVED_LEGAL},
    TenureStatus.PRE_HIRE: {TenureStatus.ACTIVE, TenureStatus.ARCHIVED_LEGAL},
    TenureStatus.ACTIVE: {TenureStatus.ON_LEAVE, TenureStatus.PRE_OFFBOARDING},
    TenureStatus.ON_LEAVE: {TenureStatus.ACTIVE, TenureStatus.PRE_OFFBOARDING},
    TenureStatus.PRE_OFFBOARDING: {TenureStatus.OFFBOARDED, TenureStatus.ACTIVE},
    TenureStatus.OFFBOARDED: {TenureStatus.ARCHIVED_LEGAL},
    TenureStatus.ARCHIVED_LEGAL: set(),
}

_TENURE_TRANSITION_EVENTS: dict[tuple[TenureStatus, TenureStatus], str] = {
    (TenureStatus.PRE_HIRE, TenureStatus.ACTIVE): HR_MEMBER_ONBOARDED,
    (TenureStatus.PRE_OFFBOARDING, TenureStatus.OFFBOARDED): HR_MEMBER_OFFBOARDED,
}


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _audit(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    actor_member_uuid: str | None,
    action: str,
    profile_uuid: str,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=actor_member_uuid,
            domain=AuditDomain.HR,
            action=action,
            resource_type="hr.employee_profile",
            resource_uuid=profile_uuid,
            audit_metadata=metadata or {},
        )
    )


# ---------------------------------------------------------------------------
# Privacy masking
# ---------------------------------------------------------------------------


# Columns the masker should never expose, regardless of caller layer
# (`deleted_at` is soft-delete bookkeeping; clients use list filters instead).
_HIDDEN_COLUMNS = frozenset({"deleted_at"})


def _allowed_layers(
    *,
    is_self: bool,
    is_manager: bool,
    is_hr_admin: bool,
) -> set[str]:
    layers: set[str] = {PRIVACY_PUBLIC}
    if is_manager:
        layers.add(PRIVACY_MANAGER)
    if is_hr_admin:
        layers.update({PRIVACY_MANAGER, PRIVACY_HR_ONLY})
    if is_self:
        layers.update({PRIVACY_MANAGER, PRIVACY_HR_ONLY, PRIVACY_SELF_ONLY})
    return layers


def _mask_profile(
    profile: EmployeeProfile,
    *,
    allowed_layers: set[str],
) -> dict[str, Any]:
    """Return a dict suitable for `EmployeeProfileOutput.model_validate(...)`.

    Columns without a `privacy` info tag (uuid, workspace_uuid, timestamps)
    are always included. Columns whose privacy layer isn't in
    `allowed_layers` come back as `None`.
    """
    out: dict[str, Any] = {}
    for col in profile.__table__.columns:
        name = col.name
        if name in _HIDDEN_COLUMNS:
            continue
        privacy = col.info.get("privacy")
        value = getattr(profile, name)
        if privacy is None or privacy in allowed_layers:
            out[name] = value
        else:
            out[name] = None
    return out


async def _resolve_caller_layers(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    profile: EmployeeProfile,
) -> set[str]:
    """Compute the caller's privacy layers for THIS profile, given the
    caller's workspace roles, manager relationship, and self relationship.
    """
    caller_roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    is_self = profile.member_uuid == caller_member_uuid
    is_manager = (
        profile.manager_member_uuid is not None
        and profile.manager_member_uuid == caller_member_uuid
    )
    is_hr_admin = is_workspace_admin(caller_roles)
    return _allowed_layers(
        is_self=is_self,
        is_manager=is_manager,
        is_hr_admin=is_hr_admin,
    )


# ---------------------------------------------------------------------------
# Internal lookups
# ---------------------------------------------------------------------------


async def _get_profile_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    profile_uuid: str,
) -> EmployeeProfile:
    res = await db.execute(
        select(EmployeeProfile).where(
            EmployeeProfile.uuid == profile_uuid,
            EmployeeProfile.workspace_uuid == workspace_uuid,
            EmployeeProfile.deleted_at.is_(None),
        )
    )
    profile = res.scalar_one_or_none()
    if not profile:
        raise _not_found("EmployeeProfile not found")
    return profile


async def _get_profile_by_member_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str,
) -> EmployeeProfile:
    res = await db.execute(
        select(EmployeeProfile).where(
            EmployeeProfile.workspace_uuid == workspace_uuid,
            EmployeeProfile.member_uuid == member_uuid,
            EmployeeProfile.deleted_at.is_(None),
        )
    )
    profile = res.scalar_one_or_none()
    if not profile:
        raise _not_found("EmployeeProfile not found for member")
    return profile


# ---------------------------------------------------------------------------
# Public service surface
# ---------------------------------------------------------------------------


async def create_employee_profile(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: EmployeeProfileCreateInput,
    db: AsyncSession,
) -> EmployeeProfileOutput:
    """HR Admin-only entry point. The Member must already exist
    (invite + accept flow lives in Workspace/Member service)."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )

    # UNIQUE(workspace, member) at the DB level guarantees 1:1; surface a
    # friendly 400 instead of letting the integrity error bubble up.
    existing = await db.execute(
        select(EmployeeProfile.uuid).where(
            EmployeeProfile.workspace_uuid == workspace_uuid,
            EmployeeProfile.member_uuid == payload.member_uuid,
            EmployeeProfile.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise _bad_request("Member already has an EmployeeProfile")

    profile = EmployeeProfile(
        workspace_uuid=workspace_uuid,
        member_uuid=payload.member_uuid,
        employment_type=payload.employment_type,
        employee_no=payload.employee_no,
        title=payload.title,
        org_unit_uuid=payload.org_unit_uuid,
        hired_at=payload.hired_at,
        manager_member_uuid=payload.manager_member_uuid,
        tenure_status=TenureStatus.PRE_HIRE,
    )
    db.add(profile)
    await db.flush()

    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.employee_profile.created",
        profile_uuid=profile.uuid,
        metadata={
            "member_uuid": payload.member_uuid,
            "employment_type": payload.employment_type.value,
        },
    )
    await db.commit()
    await db.refresh(profile)

    # Creator always gets a full HR-Admin view of the new profile.
    layers = _allowed_layers(is_self=False, is_manager=False, is_hr_admin=True)
    return EmployeeProfileOutput.model_validate(
        _mask_profile(profile, allowed_layers=layers)
    )


async def get_employee_profile(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    profile_uuid: str,
    db: AsyncSession,
) -> EmployeeProfileOutput:
    profile = await _get_profile_or_404(
        db, workspace_uuid=workspace_uuid, profile_uuid=profile_uuid
    )
    layers = await _resolve_caller_layers(
        db,
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        profile=profile,
    )
    return EmployeeProfileOutput.model_validate(
        _mask_profile(profile, allowed_layers=layers)
    )


async def list_employee_profiles(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: EmployeeProfileListFilter,
    db: AsyncSession,
) -> EmployeeProfileListOutput:
    caller_roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    is_hr_admin = is_workspace_admin(caller_roles)

    base = select(EmployeeProfile).where(
        EmployeeProfile.workspace_uuid == workspace_uuid,
        EmployeeProfile.deleted_at.is_(None),
    )
    if filters.tenure_status is not None:
        base = base.where(EmployeeProfile.tenure_status == filters.tenure_status)
    if filters.org_unit_uuid is not None:
        base = base.where(EmployeeProfile.org_unit_uuid == filters.org_unit_uuid)
    if filters.manager_member_uuid is not None:
        base = base.where(
            EmployeeProfile.manager_member_uuid == filters.manager_member_uuid
        )

    total_res = await db.execute(select(func.count()).select_from(base.subquery()))
    total = int(total_res.scalar_one())

    page_res = await db.execute(
        base.order_by(EmployeeProfile.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    profiles = list(page_res.scalars().all())

    out: list[EmployeeProfileOutput] = []
    for profile in profiles:
        is_self = profile.member_uuid == caller_member_uuid
        is_manager = (
            profile.manager_member_uuid is not None
            and profile.manager_member_uuid == caller_member_uuid
        )
        layers = _allowed_layers(
            is_self=is_self, is_manager=is_manager, is_hr_admin=is_hr_admin
        )
        out.append(
            EmployeeProfileOutput.model_validate(
                _mask_profile(profile, allowed_layers=layers)
            )
        )
    return EmployeeProfileListOutput(profiles=out, total=total)


async def update_employee_profile(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    profile_uuid: str,
    payload: EmployeeProfileUpdateInput,
    db: AsyncSession,
) -> EmployeeProfileOutput:
    """HR Admin-only. (Self-service profile editing — a much narrower
    field set — lands as a separate function in the next step.)"""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    profile = await _get_profile_or_404(
        db, workspace_uuid=workspace_uuid, profile_uuid=profile_uuid
    )
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        layers = _allowed_layers(is_self=False, is_manager=False, is_hr_admin=True)
        return EmployeeProfileOutput.model_validate(
            _mask_profile(profile, allowed_layers=layers)
        )

    for attr, value in changes.items():
        setattr(profile, attr, value)

    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.employee_profile.updated",
        profile_uuid=profile.uuid,
        metadata={"fields": sorted(changes.keys())},
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=HR_PROFILE_UPDATED,
        payload={
            "profile_uuid": profile.uuid,
            "member_uuid": profile.member_uuid,
            "fields": sorted(changes.keys()),
        },
    )
    await db.commit()
    await db.refresh(profile)

    layers = _allowed_layers(is_self=False, is_manager=False, is_hr_admin=True)
    return EmployeeProfileOutput.model_validate(
        _mask_profile(profile, allowed_layers=layers)
    )


async def transition_tenure_status(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    profile_uuid: str,
    payload: TenureTransitionInput,
    db: AsyncSession,
) -> EmployeeProfileOutput:
    """HR Admin-only. Validates the state machine and emits
    `hr.member.onboarded` / `hr.member.offboarded` on the right edges.
    """
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    profile = await _get_profile_or_404(
        db, workspace_uuid=workspace_uuid, profile_uuid=profile_uuid
    )
    prev = profile.tenure_status
    new_status = payload.new_status
    if new_status == prev:
        layers = _allowed_layers(is_self=False, is_manager=False, is_hr_admin=True)
        return EmployeeProfileOutput.model_validate(
            _mask_profile(profile, allowed_layers=layers)
        )
    if new_status not in _VALID_TENURE_TRANSITIONS[prev]:
        raise _bad_request(
            f"Illegal tenure transition {prev.value} -> {new_status.value}"
        )

    profile.tenure_status = new_status

    # When transitioning to OFFBOARDED, stamp the retention timer the
    # cleanup job (Phase 3) will key off. Default 3y; real Tier-aware
    # policy lands with the retention engine.
    if new_status == TenureStatus.OFFBOARDED:
        profile.data_retention_expires_at = datetime.now(timezone.utc).replace(  # noqa: UP017
            microsecond=0
        )

    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.tenure_status.transitioned",
        profile_uuid=profile.uuid,
        metadata={"from": prev.value, "to": new_status.value},
    )

    event_name = _TENURE_TRANSITION_EVENTS.get((prev, new_status))
    if event_name is not None:
        emit_event(
            db,
            workspace_uuid=workspace_uuid,
            event_name=event_name,
            payload={
                "profile_uuid": profile.uuid,
                "member_uuid": profile.member_uuid,
                "from": prev.value,
                "to": new_status.value,
            },
        )

    await db.commit()
    await db.refresh(profile)

    layers = _allowed_layers(is_self=False, is_manager=False, is_hr_admin=True)
    return EmployeeProfileOutput.model_validate(
        _mask_profile(profile, allowed_layers=layers)
    )


__all__ = [
    # exported for tests / other domains that need the masking primitive
    "PermissionDenied",
    "RoleName",
    "create_employee_profile",
    "get_employee_profile",
    "list_employee_profiles",
    "transition_tenure_status",
    "update_employee_profile",
]
