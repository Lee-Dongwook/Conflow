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
    HR_LEAVE_APPROVED,
    HR_LEAVE_REJECTED,
    HR_LEAVE_SUBMITTED,
    HR_MEMBER_OFFBOARDED,
    HR_MEMBER_ONBOARDED,
    HR_ONE_ON_ONE_RECORDED,
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
    LeaveRequest,
    LeaveStatus,
    OffboardingPhase,
    OffboardingReasonCode,
    OffboardingWorkflow,
    OnboardingPhase,
    OnboardingStep,
    OnboardingStepStatus,
    OnboardingWorkflow,
    OneOnOne,
    TenureStatus,
)
from .schemas import (
    EmployeeProfileCreateInput,
    EmployeeProfileListFilter,
    EmployeeProfileListOutput,
    EmployeeProfileOutput,
    EmployeeProfileUpdateInput,
    LeaveDecisionInput,
    LeaveListFilter,
    LeaveListOutput,
    LeaveOutput,
    LeaveSubmitInput,
    OffboardingListFilter,
    OffboardingListOutput,
    OffboardingOutput,
    OffboardingStartInput,
    OffboardingTransitionInput,
    OnboardingListFilter,
    OnboardingListOutput,
    OnboardingStartInput,
    OnboardingStepOutput,
    OnboardingWorkflowOutput,
    OnboardingWorkflowWithStepsOutput,
    OneOnOneCreateInput,
    OneOnOneEditInput,
    OneOnOneListFilter,
    OneOnOneListOutput,
    OneOnOneOutput,
    TenureTransitionInput,
)

_SENSITIVE_OFFBOARDING_REASONS = frozenset(
    {OffboardingReasonCode.AGREED_TERMINATION, OffboardingReasonCode.DISMISSAL}
)

_VALID_OFFBOARDING_TRANSITIONS: dict[OffboardingPhase, set[OffboardingPhase]] = {
    OffboardingPhase.DRAFT: {OffboardingPhase.PENDING_REVIEW, OffboardingPhase.IN_PROGRESS},
    OffboardingPhase.PENDING_REVIEW: {OffboardingPhase.IN_PROGRESS},
    OffboardingPhase.IN_PROGRESS: {OffboardingPhase.COMPLETED},
    OffboardingPhase.COMPLETED: set(),
}

_VALID_LEAVE_DECISIONS: frozenset[LeaveStatus] = frozenset(
    {LeaveStatus.APPROVED, LeaveStatus.REJECTED}
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


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------


def _audit_hr(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    actor_member_uuid: str | None,
    action: str,
    resource_type: str,
    resource_uuid: str,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=actor_member_uuid,
            domain=AuditDomain.HR,
            action=action,
            resource_type=resource_type,
            resource_uuid=resource_uuid,
            audit_metadata=metadata or {},
        )
    )


async def start_onboarding(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: OnboardingStartInput,
    db: AsyncSession,
) -> OnboardingWorkflowWithStepsOutput:
    """HR Admin starts a new hire's onboarding workflow with optional steps."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )

    workflow = OnboardingWorkflow(
        workspace_uuid=workspace_uuid,
        target_member_uuid=payload.target_member_uuid,
        template_uuid=payload.template_uuid,
        phase=OnboardingPhase.PENDING,
        assigned_buddy_member_uuid=payload.assigned_buddy_member_uuid,
    )
    db.add(workflow)
    await db.flush()

    steps: list[OnboardingStep] = []
    for seed in payload.steps:
        step = OnboardingStep(
            workflow_uuid=workflow.uuid,
            workspace_uuid=workspace_uuid,
            kind=seed.kind,
            target_domain=seed.target_domain,
            target_payload=seed.target_payload,
            due_date=seed.due_date,
            responsible_member_uuid=seed.responsible_member_uuid,
            step_order=seed.step_order,
        )
        db.add(step)
        steps.append(step)
    if steps:
        await db.flush()

    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.onboarding.started",
        resource_type="hr.onboarding_workflow",
        resource_uuid=workflow.uuid,
        metadata={
            "target_member_uuid": payload.target_member_uuid,
            "step_count": len(steps),
        },
    )
    await db.commit()
    await db.refresh(workflow)
    for s in steps:
        await db.refresh(s)
    return OnboardingWorkflowWithStepsOutput(
        **OnboardingWorkflowOutput.model_validate(workflow).model_dump(),
        steps=[OnboardingStepOutput.model_validate(s) for s in steps],
    )


async def list_onboardings(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: OnboardingListFilter,
    db: AsyncSession,
) -> OnboardingListOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    base = select(OnboardingWorkflow).where(
        OnboardingWorkflow.workspace_uuid == workspace_uuid,
        OnboardingWorkflow.deleted_at.is_(None),
    )
    if filters.phase is not None:
        base = base.where(OnboardingWorkflow.phase == filters.phase)
    if filters.target_member_uuid is not None:
        base = base.where(
            OnboardingWorkflow.target_member_uuid == filters.target_member_uuid
        )
    total = int((await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one())
    page = await db.execute(
        base.order_by(OnboardingWorkflow.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    return OnboardingListOutput(
        workflows=[OnboardingWorkflowOutput.model_validate(w) for w in page.scalars().all()],
        total=total,
    )


async def get_onboarding_with_steps(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    workflow_uuid: str,
    db: AsyncSession,
) -> OnboardingWorkflowWithStepsOutput:
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    wf_res = await db.execute(
        select(OnboardingWorkflow).where(
            OnboardingWorkflow.uuid == workflow_uuid,
            OnboardingWorkflow.workspace_uuid == workspace_uuid,
            OnboardingWorkflow.deleted_at.is_(None),
        )
    )
    wf = wf_res.scalar_one_or_none()
    if wf is None:
        raise _not_found("OnboardingWorkflow not found")

    # Read access: target, assigned buddy, HR Admin.
    if not (
        wf.target_member_uuid == caller_member_uuid
        or wf.assigned_buddy_member_uuid == caller_member_uuid
        or is_workspace_admin(roles)
    ):
        raise PermissionDenied("Only the target, buddy, or HR Admin may read")

    step_res = await db.execute(
        select(OnboardingStep)
        .where(OnboardingStep.workflow_uuid == workflow_uuid)
        .order_by(OnboardingStep.step_order)
    )
    steps = list(step_res.scalars().all())
    return OnboardingWorkflowWithStepsOutput(
        **OnboardingWorkflowOutput.model_validate(wf).model_dump(),
        steps=[OnboardingStepOutput.model_validate(s) for s in steps],
    )


async def mark_step_done(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    step_uuid: str,
    db: AsyncSession,
) -> OnboardingStepOutput:
    """Mark an OnboardingStep done. When the workflow's final step lands,
    flips phase to COMPLETED, transitions the EmployeeProfile to ACTIVE,
    and emits HR_MEMBER_ONBOARDED.
    """
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    step_res = await db.execute(
        select(OnboardingStep).where(
            OnboardingStep.uuid == step_uuid,
            OnboardingStep.workspace_uuid == workspace_uuid,
        )
    )
    step = step_res.scalar_one_or_none()
    if step is None:
        raise _not_found("OnboardingStep not found")

    if not (
        step.responsible_member_uuid == caller_member_uuid
        or is_workspace_admin(roles)
    ):
        raise PermissionDenied("Only the responsible member or HR Admin may mark done")
    if step.status == OnboardingStepStatus.DONE:
        return OnboardingStepOutput.model_validate(step)

    step.status = OnboardingStepStatus.DONE

    # Recompute workflow progress + completion.
    wf = await db.get(OnboardingWorkflow, step.workflow_uuid)
    if wf is None:
        raise _not_found("OnboardingWorkflow not found")

    counts_res = await db.execute(
        select(OnboardingStep.status, func.count())
        .where(OnboardingStep.workflow_uuid == wf.uuid)
        .group_by(OnboardingStep.status)
    )
    by_status = {s: c for s, c in counts_res.all()}
    total_steps = sum(by_status.values())
    done_steps = (
        by_status.get(OnboardingStepStatus.DONE, 0)
        + by_status.get(OnboardingStepStatus.SKIPPED, 0)
    )
    wf.progress_pct = int(round(100 * done_steps / total_steps)) if total_steps else 100
    if wf.phase == OnboardingPhase.PENDING:
        wf.phase = OnboardingPhase.IN_PROGRESS
        wf.started_at = datetime.now(timezone.utc)  # noqa: UP017

    completed = total_steps > 0 and done_steps == total_steps
    if completed and wf.phase != OnboardingPhase.COMPLETED:
        wf.phase = OnboardingPhase.COMPLETED
        wf.completed_at = datetime.now(timezone.utc)  # noqa: UP017
        # Flip EmployeeProfile to ACTIVE if it's currently PRE_HIRE.
        prof_res = await db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.workspace_uuid == workspace_uuid,
                EmployeeProfile.member_uuid == wf.target_member_uuid,
                EmployeeProfile.deleted_at.is_(None),
            )
        )
        profile = prof_res.scalar_one_or_none()
        if profile is not None and profile.tenure_status == TenureStatus.PRE_HIRE:
            profile.tenure_status = TenureStatus.ACTIVE

        emit_event(
            db,
            workspace_uuid=workspace_uuid,
            event_name=HR_MEMBER_ONBOARDED,
            payload={
                "workflow_uuid": wf.uuid,
                "member_uuid": wf.target_member_uuid,
                "from": "pre_hire",
                "to": "active",
            },
        )

    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.onboarding.step_completed",
        resource_type="hr.onboarding_step",
        resource_uuid=step.uuid,
        metadata={"workflow_uuid": wf.uuid, "progress_pct": wf.progress_pct},
    )
    await db.commit()
    await db.refresh(step)
    return OnboardingStepOutput.model_validate(step)


# ---------------------------------------------------------------------------
# Offboarding
# ---------------------------------------------------------------------------


async def start_offboarding(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: OffboardingStartInput,
    db: AsyncSession,
) -> OffboardingOutput:
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    requires_review = payload.reason_code in _SENSITIVE_OFFBOARDING_REASONS
    wf = OffboardingWorkflow(
        workspace_uuid=workspace_uuid,
        target_member_uuid=payload.target_member_uuid,
        reason_code=payload.reason_code,
        requires_labor_review=requires_review,
        effective_date=payload.effective_date,
        phase=(
            OffboardingPhase.PENDING_REVIEW
            if requires_review
            else OffboardingPhase.DRAFT
        ),
        data_retention_policy=payload.data_retention_policy,
    )
    db.add(wf)
    await db.flush()

    # Flip EmployeeProfile.tenure_status to PRE_OFFBOARDING if ACTIVE/ON_LEAVE.
    prof_res = await db.execute(
        select(EmployeeProfile).where(
            EmployeeProfile.workspace_uuid == workspace_uuid,
            EmployeeProfile.member_uuid == payload.target_member_uuid,
            EmployeeProfile.deleted_at.is_(None),
        )
    )
    profile = prof_res.scalar_one_or_none()
    if profile is not None and profile.tenure_status in (
        TenureStatus.ACTIVE,
        TenureStatus.ON_LEAVE,
    ):
        profile.tenure_status = TenureStatus.PRE_OFFBOARDING

    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.offboarding.started",
        resource_type="hr.offboarding_workflow",
        resource_uuid=wf.uuid,
        metadata={
            "reason_code": payload.reason_code.value,
            "requires_labor_review": requires_review,
            "effective_date": payload.effective_date.isoformat(),
        },
    )
    await db.commit()
    await db.refresh(wf)
    return OffboardingOutput.model_validate(wf)


async def transition_offboarding_phase(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    workflow_uuid: str,
    payload: OffboardingTransitionInput,
    db: AsyncSession,
) -> OffboardingOutput:
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    wf_res = await db.execute(
        select(OffboardingWorkflow).where(
            OffboardingWorkflow.uuid == workflow_uuid,
            OffboardingWorkflow.workspace_uuid == workspace_uuid,
            OffboardingWorkflow.deleted_at.is_(None),
        )
    )
    wf = wf_res.scalar_one_or_none()
    if wf is None:
        raise _not_found("OffboardingWorkflow not found")

    prev = wf.phase
    new = payload.new_phase
    if new == prev:
        return OffboardingOutput.model_validate(wf)
    if new not in _VALID_OFFBOARDING_TRANSITIONS[prev]:
        raise _bad_request(f"Illegal offboarding transition {prev.value} -> {new.value}")

    wf.phase = new
    if payload.final_payment_status is not None:
        wf.final_payment_status = payload.final_payment_status

    if new == OffboardingPhase.COMPLETED:
        # Final tenure transition.
        prof_res = await db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.workspace_uuid == workspace_uuid,
                EmployeeProfile.member_uuid == wf.target_member_uuid,
                EmployeeProfile.deleted_at.is_(None),
            )
        )
        profile = prof_res.scalar_one_or_none()
        if profile is not None and profile.tenure_status == TenureStatus.PRE_OFFBOARDING:
            profile.tenure_status = TenureStatus.OFFBOARDED
            profile.data_retention_expires_at = datetime.now(timezone.utc).replace(  # noqa: UP017
                microsecond=0
            )

        emit_event(
            db,
            workspace_uuid=workspace_uuid,
            event_name=HR_MEMBER_OFFBOARDED,
            payload={
                "workflow_uuid": wf.uuid,
                "member_uuid": wf.target_member_uuid,
                "reason_code": wf.reason_code.value,
                "effective_date": wf.effective_date.isoformat(),
            },
        )

    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.offboarding.transitioned",
        resource_type="hr.offboarding_workflow",
        resource_uuid=wf.uuid,
        metadata={"from": prev.value, "to": new.value},
    )
    await db.commit()
    await db.refresh(wf)
    return OffboardingOutput.model_validate(wf)


async def list_offboardings(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: OffboardingListFilter,
    db: AsyncSession,
) -> OffboardingListOutput:
    """HR Admin only — offboarding rows expose sensitive `reason_code`."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    base = select(OffboardingWorkflow).where(
        OffboardingWorkflow.workspace_uuid == workspace_uuid,
        OffboardingWorkflow.deleted_at.is_(None),
    )
    if filters.phase is not None:
        base = base.where(OffboardingWorkflow.phase == filters.phase)
    if filters.requires_labor_review is not None:
        base = base.where(
            OffboardingWorkflow.requires_labor_review == filters.requires_labor_review
        )
    total = int((await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one())
    page = await db.execute(
        base.order_by(OffboardingWorkflow.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    return OffboardingListOutput(
        workflows=[OffboardingOutput.model_validate(w) for w in page.scalars().all()],
        total=total,
    )


# ---------------------------------------------------------------------------
# OneOnOne
# ---------------------------------------------------------------------------


async def create_one_on_one(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: OneOnOneCreateInput,
    db: AsyncSession,
) -> OneOnOneOutput:
    """Caller is the manager. Schedules a 1:1 with `report_member_uuid`."""
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    if payload.report_member_uuid == caller_member_uuid:
        raise _bad_request("Cannot schedule a 1:1 with yourself")
    one_on_one = OneOnOne(
        workspace_uuid=workspace_uuid,
        manager_member_uuid=caller_member_uuid,
        report_member_uuid=payload.report_member_uuid,
        scheduled_at=payload.scheduled_at,
        visibility=payload.visibility,
    )
    db.add(one_on_one)
    await db.flush()

    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.one_on_one.created",
        resource_type="hr.one_on_one",
        resource_uuid=one_on_one.uuid,
        metadata={
            "manager": caller_member_uuid,
            "report": payload.report_member_uuid,
        },
    )
    await db.commit()
    await db.refresh(one_on_one)
    return OneOnOneOutput.model_validate(one_on_one)


async def edit_one_on_one(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    one_on_one_uuid: str,
    payload: OneOnOneEditInput,
    db: AsyncSession,
) -> OneOnOneOutput:
    """Manager (and report when visibility allows) may edit. Admin/Owner
    cannot bypass — that's a DB-level RLS rule landing in a follow-up.
    `held_at` first-time set emits `hr.one_on_one.recorded` (A2UI keyword
    payload only — never raw notes).
    """
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    oo_res = await db.execute(
        select(OneOnOne).where(
            OneOnOne.uuid == one_on_one_uuid,
            OneOnOne.workspace_uuid == workspace_uuid,
        )
    )
    oo = oo_res.scalar_one_or_none()
    if oo is None:
        raise _not_found("OneOnOne not found")

    is_manager = oo.manager_member_uuid == caller_member_uuid
    is_report = oo.report_member_uuid == caller_member_uuid
    if not (is_manager or is_report):
        raise PermissionDenied("Only the manager or report may edit this 1:1")

    changes = payload.model_dump(exclude_unset=True)
    held_was_none = oo.held_at is None

    for attr, value in changes.items():
        setattr(oo, attr, value)

    if held_was_none and oo.held_at is not None:
        # First time the meeting is marked held — emit A2UI-friendly event.
        emit_event(
            db,
            workspace_uuid=workspace_uuid,
            event_name=HR_ONE_ON_ONE_RECORDED,
            payload={
                "one_on_one_uuid": oo.uuid,
                "manager_member_uuid": oo.manager_member_uuid,
                "report_member_uuid": oo.report_member_uuid,
                "held_at": oo.held_at.isoformat(),
                # NOTE: notes_md is intentionally NOT included.
                "action_item_count": len(oo.action_items or []),
            },
        )

    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.one_on_one.edited",
        resource_type="hr.one_on_one",
        resource_uuid=oo.uuid,
        metadata={"fields": sorted(changes.keys())},
    )
    await db.commit()
    await db.refresh(oo)
    return OneOnOneOutput.model_validate(oo)


async def list_my_one_on_ones(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: OneOnOneListFilter,
    db: AsyncSession,
) -> OneOnOneListOutput:
    """Returns 1:1s where caller is manager OR report — never others'."""
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    base = select(OneOnOne).where(
        OneOnOne.workspace_uuid == workspace_uuid,
        (OneOnOne.manager_member_uuid == caller_member_uuid)
        | (OneOnOne.report_member_uuid == caller_member_uuid),
    )
    if filters.other_party_member_uuid is not None:
        base = base.where(
            (OneOnOne.manager_member_uuid == filters.other_party_member_uuid)
            | (OneOnOne.report_member_uuid == filters.other_party_member_uuid)
        )
    total = int((await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one())
    page = await db.execute(
        base.order_by(OneOnOne.scheduled_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    return OneOnOneListOutput(
        one_on_ones=[OneOnOneOutput.model_validate(o) for o in page.scalars().all()],
        total=total,
    )


# ---------------------------------------------------------------------------
# LeaveRequest
# ---------------------------------------------------------------------------


async def submit_leave(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: LeaveSubmitInput,
    db: AsyncSession,
) -> LeaveOutput:
    """Caller submits a leave for themselves. Status enters SUBMITTED."""
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    if payload.end_date < payload.start_date:
        raise _bad_request("end_date must be >= start_date")

    leave = LeaveRequest(
        workspace_uuid=workspace_uuid,
        requester_member_uuid=caller_member_uuid,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        half_day=payload.half_day,
        reason_md=payload.reason_md,
        attachments=payload.attachments,
        status=LeaveStatus.SUBMITTED,
    )
    db.add(leave)
    await db.flush()
    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="hr.leave.submitted",
        resource_type="hr.leave_request",
        resource_uuid=leave.uuid,
        metadata={"leave_type": payload.leave_type.value},
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=HR_LEAVE_SUBMITTED,
        payload={
            "leave_uuid": leave.uuid,
            "requester_member_uuid": caller_member_uuid,
            "leave_type": payload.leave_type.value,
            "start_date": payload.start_date.isoformat(),
            "end_date": payload.end_date.isoformat(),
        },
    )
    await db.commit()
    await db.refresh(leave)
    return LeaveOutput.model_validate(leave)


async def decide_leave(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    leave_uuid: str,
    payload: LeaveDecisionInput,
    db: AsyncSession,
) -> LeaveOutput:
    """Manager of the requester (per EmployeeProfile.manager_member_uuid)
    or HR Admin approves/rejects. SUBMITTED → APPROVED/REJECTED only.
    """
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    if payload.status not in _VALID_LEAVE_DECISIONS:
        raise _bad_request("Decision must be APPROVED or REJECTED")

    leave_res = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.uuid == leave_uuid,
            LeaveRequest.workspace_uuid == workspace_uuid,
            LeaveRequest.deleted_at.is_(None),
        )
    )
    leave = leave_res.scalar_one_or_none()
    if leave is None:
        raise _not_found("LeaveRequest not found")
    if leave.status != LeaveStatus.SUBMITTED:
        raise _bad_request(f"Cannot decide a leave in status {leave.status.value}")

    # Approver = HR Admin OR the requester's manager (from EmployeeProfile).
    if not is_workspace_admin(roles):
        prof_res = await db.execute(
            select(EmployeeProfile.manager_member_uuid).where(
                EmployeeProfile.workspace_uuid == workspace_uuid,
                EmployeeProfile.member_uuid == leave.requester_member_uuid,
                EmployeeProfile.deleted_at.is_(None),
            )
        )
        manager_uuid = prof_res.scalar_one_or_none()
        if manager_uuid != caller_member_uuid:
            raise PermissionDenied(
                "Only the requester's manager or HR Admin may decide"
            )

    leave.status = payload.status
    leave.approver_member_uuid = caller_member_uuid

    event_name = (
        HR_LEAVE_APPROVED if payload.status == LeaveStatus.APPROVED else HR_LEAVE_REJECTED
    )
    _audit_hr(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action=event_name,  # also serves as audit action name
        resource_type="hr.leave_request",
        resource_uuid=leave.uuid,
        metadata={
            "requester_member_uuid": leave.requester_member_uuid,
            "decision": payload.status.value,
        },
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=event_name,
        payload={
            "leave_uuid": leave.uuid,
            "requester_member_uuid": leave.requester_member_uuid,
            "approver_member_uuid": caller_member_uuid,
            "leave_type": leave.leave_type.value,
        },
    )
    await db.commit()
    await db.refresh(leave)
    return LeaveOutput.model_validate(leave)


async def list_leaves(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: LeaveListFilter,
    db: AsyncSession,
) -> LeaveListOutput:
    """Caller sees their own + (if HR Admin) all + (if manager of requester
    via EmployeeProfile) their reports'. Alpha: serve own + HR-Admin all;
    manager-of-requester scoping lands once Project-style relationship
    queries are needed.
    """
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    base = select(LeaveRequest).where(
        LeaveRequest.workspace_uuid == workspace_uuid,
        LeaveRequest.deleted_at.is_(None),
    )
    if not is_workspace_admin(roles):
        # Scope to caller's own leaves unless an explicit override is
        # made by an Admin via filters.requester_member_uuid.
        base = base.where(LeaveRequest.requester_member_uuid == caller_member_uuid)
    elif filters.requester_member_uuid is not None:
        base = base.where(
            LeaveRequest.requester_member_uuid == filters.requester_member_uuid
        )
    if filters.status is not None:
        base = base.where(LeaveRequest.status == filters.status)

    total = int((await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one())
    page = await db.execute(
        base.order_by(LeaveRequest.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    return LeaveListOutput(
        leaves=[LeaveOutput.model_validate(le) for le in page.scalars().all()],
        total=total,
    )


__all__ = [
    "PermissionDenied",
    "RoleName",
    "create_employee_profile",
    "create_one_on_one",
    "decide_leave",
    "edit_one_on_one",
    "get_employee_profile",
    "get_onboarding_with_steps",
    "list_employee_profiles",
    "list_leaves",
    "list_my_one_on_ones",
    "list_offboardings",
    "list_onboardings",
    "mark_step_done",
    "start_offboarding",
    "start_onboarding",
    "submit_leave",
    "transition_offboarding_phase",
    "transition_tenure_status",
    "update_employee_profile",
]
