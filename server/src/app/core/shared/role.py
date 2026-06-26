from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class RoleName(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"
    EXTERNAL = "external"


class RoleScope(enum.Enum):
    WORKSPACE = "workspace"
    RESOURCE = "resource"


class Role(Base, AutoUUIDMixin):
    """Workspace-scoped role definition (the "single permission model").

    Five fixed names per docs/02-product/domain-overview.md. Domain-specific
    permission tables are forbidden (Watch List #2). All gating lives in
    `permissions` JSONB or the Tool Registry; never in domain service code.
    """

    __tablename__ = "roles"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )

    name: Mapped[RoleName] = mapped_column(
        Enum(
            RoleName,
            name="role_name",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    scope_type: Mapped[RoleScope] = mapped_column(
        Enum(
            RoleScope,
            name="role_scope",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=RoleScope.WORKSPACE,
        nullable=False,
    )

    # Phase 0 alpha: empty {} until the permission DSL is settled
    # (docs/04-architecture/a2ui-strategy.md Tool Registry).
    permissions: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_uuid",
            "name",
            "scope_type",
            name="uq_roles_workspace_name_scope",
        ),
        Index("idx_roles_workspace", "workspace_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
