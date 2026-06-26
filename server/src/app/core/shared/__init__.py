"""Shared Core entities referenced by all domains but owned by none.

Per docs/02-product/domain-overview.md and docs/04-architecture/data-model.md:
- Workspace: single-tenant boundary
- Member: a person within a Workspace (Phase 0)
- Role / RoleAssignment: single permission model (Phase 0)
- AuditLog: unified audit trail (Phase 0)
- EntityLink: cross-domain reference (Phase 0)

Domains read these but never mutate them directly.
"""

from .member import Member, MemberStatus
from .workspace import Workspace, WorkspaceRegion, WorkspaceTier

__all__ = [
    "Member",
    "MemberStatus",
    "Workspace",
    "WorkspaceRegion",
    "WorkspaceTier",
]
