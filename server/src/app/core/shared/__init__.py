"""Shared Core entities referenced by all domains but owned by none.

Per docs/02-product/domain-overview.md and docs/04-architecture/data-model.md:
- Workspace: single-tenant boundary
- Member: a person within a Workspace (Phase 0)
- Role / RoleAssignment: single permission model (Phase 0)
- AuditLog: unified audit trail (Phase 0)
- EntityLink: cross-domain reference (Phase 0)

Domains read these but never mutate them directly.
"""

from .audit_log import AuditDomain, AuditLog
from .entity_link import EntityLink, EntityLinkKind
from .event_outbox import EventOutbox
from .member import Member, MemberStatus
from .role import Role, RoleName, RoleScope
from .role_assignment import RoleAssignment
from .service import (
    MemberInviteInput,
    MemberInviteOutput,
    MemberReadOutput,
    WorkspaceCreateInput,
    WorkspaceReadOutput,
    accept_invitation,
    create_workspace,
    invite_member,
)
from .workspace import Workspace, WorkspaceRegion, WorkspaceTier

__all__ = [
    "AuditDomain",
    "AuditLog",
    "EntityLink",
    "EntityLinkKind",
    "EventOutbox",
    "Member",
    "MemberInviteInput",
    "MemberInviteOutput",
    "MemberReadOutput",
    "MemberStatus",
    "Role",
    "RoleAssignment",
    "RoleName",
    "RoleScope",
    "Workspace",
    "WorkspaceCreateInput",
    "WorkspaceReadOutput",
    "WorkspaceRegion",
    "WorkspaceTier",
    "accept_invitation",
    "create_workspace",
    "invite_member",
]
