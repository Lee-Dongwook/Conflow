from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class MemberStatus(enum.Enum):
    INVITED = "invited"
    ACTIVE = "active"
    DISABLED = "disabled"
    EXTERNAL = "external"


class Member(Base, AutoUUIDMixin):
    """A person within a Workspace.

    `Member.uuid` is the single identifier used by every domain
    (PM `assignee_uuid`, Comms `author_uuid`, HR `employee_uuid`).
    A human can exist in multiple workspaces as different Members —
    "one person = one workspace = one Member" is enforced at workspace scope.
    """

    __tablename__ = "members"

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

    # Nullable: invited members and external collaborators (e.g. 노무사) may not
    # have a `users` row yet. Bound when the invite is accepted or the external
    # collaborator authenticates through their own workspace.
    user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid"),
        nullable=True,
    )

    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[MemberStatus] = mapped_column(
        Enum(
            MemberStatus,
            name="member_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=MemberStatus.INVITED,
        nullable=False,
    )

    joined_at: Mapped[datetime | None] = mapped_column(
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
        UniqueConstraint(
            "workspace_uuid",
            "user_uuid",
            name="uq_members_workspace_user",
        ),
        UniqueConstraint(
            "workspace_uuid",
            "email",
            name="uq_members_workspace_email",
        ),
        Index("idx_members_workspace_status", "workspace_uuid", "status"),
        Index("idx_members_workspace_email", "workspace_uuid", "email"),
        Index("idx_members_user", "user_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_external(self) -> bool:
        return self.status == MemberStatus.EXTERNAL
