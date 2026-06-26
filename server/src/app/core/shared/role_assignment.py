from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class RoleAssignment(Base, AutoUUIDMixin):
    """Binds a Member to a Role, optionally scoped to a single resource.

    `workspace_uuid` is duplicated here (not just derived through Role)
    so RLS policies can filter without a join — see
    docs/04-architecture/data-model.md "RLS 정책 패턴".

    Resource-scoped assignments (`resource_type` / `resource_uuid` both set)
    are how external collaborators (e.g. 노무사) get access to a single
    document or channel without joining the workspace as a full Member.
    """

    __tablename__ = "role_assignments"

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

    member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )

    role_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("roles.uuid"),
        nullable=False,
    )

    # Both NULL → workspace-wide assignment.
    # Both set → resource-scoped (external collaborator pattern).
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # security-compliance.md: external assignments default to 1y,
    # alarm at 90d before expiry. NULL = no expiry (workspace members).
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
        Index("idx_role_assignments_member", "member_uuid"),
        Index("idx_role_assignments_role", "role_uuid"),
        Index(
            "idx_role_assignments_member_resource",
            "member_uuid",
            "resource_type",
            "resource_uuid",
        ),
        Index("idx_role_assignments_workspace", "workspace_uuid"),
        Index("idx_role_assignments_expires", "expires_at"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_resource_scoped(self) -> bool:
        return self.resource_type is not None and self.resource_uuid is not None
