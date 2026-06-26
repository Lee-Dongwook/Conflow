"""Workspace lifecycle service.

Owns the only legal way to create a Workspace: a single transaction that
also seeds the five canonical workspace-scoped Roles and assigns OWNER
to the creator. Any other Workspace insertion path bypasses the single
permission model and is forbidden.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...user.model import User
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


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


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
