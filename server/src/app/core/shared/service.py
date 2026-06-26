"""Workspace lifecycle service.

Owns the only legal way to create a Workspace: a single transaction that
also seeds the five canonical workspace-scoped Roles and assigns OWNER
to the creator. Any other Workspace insertion path bypasses the single
permission model and is forbidden.

Also owns Member invitation / acceptance — the only legal way to add new
Members. Direct `members` insertion is forbidden (skips role assignment,
audit, and the invite/email-match security check).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...user.model import User
from ..events import (
    WORKSPACE_MEMBER_INVITED,
    WORKSPACE_MEMBER_JOINED,
    emit_event,
)
from ..permissions import require_workspace_admin
from .audit_log import AuditDomain, AuditLog
from .member import Member, MemberStatus
from .role import Role, RoleName, RoleScope
from .role_assignment import RoleAssignment
from .workspace import Workspace, WorkspaceRegion, WorkspaceTier


class WorkspaceCreateInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9-]*$")
    tier: WorkspaceTier = WorkspaceTier.FREE
    region: WorkspaceRegion = WorkspaceRegion.KR


class WorkspaceReadOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    slug: str
    tier: WorkspaceTier
    region: WorkspaceRegion
    created_at: datetime
    updated_at: datetime


# OWNER is never assigned via invite — only by Workspace creation.
# EXTERNAL goes through a dedicated resource-scoped flow (Phase 3 노무사).
_INVITABLE_ROLES: frozenset[RoleName] = frozenset(
    {RoleName.ADMIN, RoleName.MEMBER, RoleName.GUEST}
)


class MemberInviteInput(BaseModel):
    email: EmailStr
    display_name: str | None = Field(default=None, max_length=64)
    role_name: RoleName = RoleName.MEMBER


class MemberInviteOutput(BaseModel):
    """Alpha-phase output: `invite_url` is a placeholder. Phase 1 will
    sign a token + email-send via the integrations layer.
    """

    member_uuid: str
    email: EmailStr
    role_name: RoleName
    invite_url: str


class MemberReadOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    user_uuid: str | None
    display_name: str
    email: str
    status: MemberStatus
    joined_at: datetime | None


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def create_workspace(
    *,
    creator_user_uuid: str,
    payload: WorkspaceCreateInput,
    db: AsyncSession,
) -> WorkspaceReadOutput:
    """Create a Workspace, its five canonical Roles, the creator's Member
    row, and an OWNER RoleAssignment — in a single transaction.

    The creator must already exist in `users` (Supabase signup).
    """
    user = await db.get(User, creator_user_uuid)
    if user is None or user.deleted_at is not None:
        raise _bad_request("Creator user not found")

    workspace = Workspace(
        name=payload.name,
        slug=payload.slug,
        tier=payload.tier,
        region=payload.region,
    )
    db.add(workspace)
    await db.flush()

    creator_member = Member(
        workspace_uuid=workspace.uuid,
        user_uuid=creator_user_uuid,
        display_name=user.name,
        email=user.email,
        status=MemberStatus.ACTIVE,
        joined_at=workspace.created_at,
    )
    db.add(creator_member)
    await db.flush()

    # Seed the five canonical workspace-scoped roles.
    # `permissions={}` is intentional — the permission DSL lives in the
    # Tool Registry (a2ui-strategy.md), not in inlined service code.
    role_by_name: dict[RoleName, Role] = {}
    for role_name in (
        RoleName.OWNER,
        RoleName.ADMIN,
        RoleName.MEMBER,
        RoleName.GUEST,
        RoleName.EXTERNAL,
    ):
        role = Role(
            workspace_uuid=workspace.uuid,
            name=role_name,
            scope_type=RoleScope.WORKSPACE,
            permissions={},
        )
        db.add(role)
        role_by_name[role_name] = role
    await db.flush()

    db.add(
        RoleAssignment(
            workspace_uuid=workspace.uuid,
            member_uuid=creator_member.uuid,
            role_uuid=role_by_name[RoleName.OWNER].uuid,
        )
    )

    db.add(
        AuditLog(
            workspace_uuid=workspace.uuid,
            actor_member_uuid=creator_member.uuid,
            domain=AuditDomain.SYSTEM,
            action="workspace.created",
            resource_type="core.workspace",
            resource_uuid=workspace.uuid,
            audit_metadata={
                "tier": workspace.tier.value,
                "region": workspace.region.value,
                "creator_user_uuid": creator_user_uuid,
            },
        )
    )

    await db.commit()
    await db.refresh(workspace)
    return WorkspaceReadOutput.model_validate(workspace)


# ---------------------------------------------------------------------------
# Member invitation / acceptance
# ---------------------------------------------------------------------------


async def invite_member(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: MemberInviteInput,
    db: AsyncSession,
) -> MemberInviteOutput:
    """Workspace Admin invites a person by email. Creates an `INVITED`
    Member row + RoleAssignment in one transaction. The invitee accepts
    by hitting `accept_invitation` after Supabase signup with the same email.
    """
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )

    if payload.role_name not in _INVITABLE_ROLES:
        raise _bad_request(
            f"Role {payload.role_name.value} is not invitable via this flow"
        )

    # UNIQUE(workspace, email) at the DB level would also catch this, but a
    # friendly 400 beats an integrity error in the API response.
    dup = await db.execute(
        select(Member).where(
            Member.workspace_uuid == workspace_uuid,
            Member.email == str(payload.email),
            Member.deleted_at.is_(None),
        )
    )
    if dup.scalar_one_or_none() is not None:
        raise _bad_request(f"Email {payload.email} is already invited or a member")

    role_res = await db.execute(
        select(Role).where(
            Role.workspace_uuid == workspace_uuid,
            Role.name == payload.role_name,
            Role.scope_type == RoleScope.WORKSPACE,
            Role.deleted_at.is_(None),
        )
    )
    role = role_res.scalar_one_or_none()
    if role is None:
        raise _bad_request(
            f"Role {payload.role_name.value} not seeded in this workspace"
        )

    member = Member(
        workspace_uuid=workspace_uuid,
        user_uuid=None,
        display_name=payload.display_name or str(payload.email).split("@", 1)[0],
        email=str(payload.email),
        status=MemberStatus.INVITED,
    )
    db.add(member)
    await db.flush()

    db.add(
        RoleAssignment(
            workspace_uuid=workspace_uuid,
            member_uuid=member.uuid,
            role_uuid=role.uuid,
        )
    )

    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=caller_member_uuid,
            domain=AuditDomain.SYSTEM,
            action="workspace.member.invited",
            resource_type="core.member",
            resource_uuid=member.uuid,
            audit_metadata={
                "email": str(payload.email),
                "role": payload.role_name.value,
            },
        )
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=WORKSPACE_MEMBER_INVITED,
        payload={
            "member_uuid": member.uuid,
            "email": str(payload.email),
            "role": payload.role_name.value,
            "invited_by_member_uuid": caller_member_uuid,
        },
    )

    await db.commit()
    await db.refresh(member)

    # Placeholder URL — Phase 1 wires this to a signed token + email-send.
    invite_url = f"/workspaces/{workspace_uuid}/members/{member.uuid}/accept"
    return MemberInviteOutput(
        member_uuid=member.uuid,
        email=member.email,
        role_name=payload.role_name,
        invite_url=invite_url,
    )


async def accept_invitation(
    *,
    workspace_uuid: str,
    invited_member_uuid: str,
    caller_user_uuid: str,
    db: AsyncSession,
) -> MemberReadOutput:
    """Bind an INVITED Member row to the caller's User account.

    Security: the caller's User.email must match the invited Member's email.
    This blocks invite-URL leakage from being exploited by a different
    signed-up account.
    """
    res = await db.execute(
        select(Member).where(
            Member.uuid == invited_member_uuid,
            Member.workspace_uuid == workspace_uuid,
            Member.status == MemberStatus.INVITED,
            Member.user_uuid.is_(None),
            Member.deleted_at.is_(None),
        )
    )
    member = res.scalar_one_or_none()
    if member is None:
        raise _not_found("Invitation not found or already accepted")

    user = await db.get(User, caller_user_uuid)
    if user is None or user.deleted_at is not None:
        raise _bad_request("Caller user not found")
    if user.email.lower() != member.email.lower():
        raise _forbidden("Invitation email does not match the signed-in account")

    member.user_uuid = caller_user_uuid
    member.status = MemberStatus.ACTIVE
    member.joined_at = datetime.now(timezone.utc)  # noqa: UP017

    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=member.uuid,
            domain=AuditDomain.SYSTEM,
            action="workspace.member.joined",
            resource_type="core.member",
            resource_uuid=member.uuid,
            audit_metadata={"user_uuid": caller_user_uuid},
        )
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=WORKSPACE_MEMBER_JOINED,
        payload={
            "member_uuid": member.uuid,
            "user_uuid": caller_user_uuid,
            "email": member.email,
        },
    )

    await db.commit()
    await db.refresh(member)
    return MemberReadOutput.model_validate(member)
