"""Permission helpers backed by Role + RoleAssignment.

Single permission model (docs/02-product/domain-overview.md): every domain
service consults this module instead of growing its own permission table.
Watch List #2 — once a domain inlines a tier/role check inside its service
function, the differentiation promise breaks.

Resource-scoped checks (e.g. "노무사 X has access to Document Y") will land
alongside the Documents domain; this file ships the workspace-scoped checks
needed by PM and Comms.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .shared import Member, MemberStatus, Role, RoleAssignment, RoleName, RoleScope


class PermissionDenied(HTTPException):
    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


_ADMIN_ROLES: frozenset[RoleName] = frozenset({RoleName.OWNER, RoleName.ADMIN})
_WRITE_ROLES: frozenset[RoleName] = frozenset(
    {RoleName.OWNER, RoleName.ADMIN, RoleName.MEMBER}
)


async def get_workspace_role_names(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str,
) -> set[RoleName]:
    """All workspace-scoped roles the (ACTIVE) member holds, filtered by
    `expires_at` and soft deletes. Empty set means no workspace permission.
    """
    now = datetime.now(timezone.utc)  # noqa: UP017
    res = await db.execute(
        select(Role.name)
        .join(RoleAssignment, RoleAssignment.role_uuid == Role.uuid)
        .join(Member, Member.uuid == RoleAssignment.member_uuid)
        .where(
            RoleAssignment.workspace_uuid == workspace_uuid,
            RoleAssignment.member_uuid == member_uuid,
            RoleAssignment.deleted_at.is_(None),
            Role.workspace_uuid == workspace_uuid,
            Role.deleted_at.is_(None),
            Role.scope_type == RoleScope.WORKSPACE,
            Member.status == MemberStatus.ACTIVE,
            Member.deleted_at.is_(None),
            or_(
                RoleAssignment.expires_at.is_(None),
                RoleAssignment.expires_at > now,
            ),
        )
    )
    return {row[0] for row in res.all()}


def is_workspace_admin(roles: set[RoleName]) -> bool:
    return bool(roles & _ADMIN_ROLES)


def is_workspace_writer(roles: set[RoleName]) -> bool:
    """Member, Admin, or Owner — i.e. anyone whose default write scope is
    the whole workspace (not Guest, not External)."""
    return bool(roles & _WRITE_ROLES)


async def require_workspace_member(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str,
) -> set[RoleName]:
    """Caller must hold at least one workspace-scoped role (any of
    owner/admin/member/guest). External-only callers are rejected here —
    they reach resources through resource-scoped assignments instead.
    """
    roles = await get_workspace_role_names(
        db, workspace_uuid=workspace_uuid, member_uuid=member_uuid
    )
    if not roles:
        raise PermissionDenied("Workspace membership required")
    return roles


async def require_workspace_writer(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str,
) -> set[RoleName]:
    """Caller must be Member or higher (no Guest, no External)."""
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=member_uuid
    )
    if not is_workspace_writer(roles):
        raise PermissionDenied("Workspace Member or higher required")
    return roles


async def require_workspace_admin(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str,
) -> set[RoleName]:
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=member_uuid
    )
    if not is_workspace_admin(roles):
        raise PermissionDenied("Workspace Admin required")
    return roles
