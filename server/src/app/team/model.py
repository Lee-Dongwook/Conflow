from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..user.model import User


class TeamMemberRole(enum.Enum):
    """Role within a team (not the same as global UserRole)."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Team(Base, AutoUUIDMixin):
    """Team workspace; members are linked via TeamMembership (N:M with User)."""

    __tablename__ = "teams"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    memberships: Mapped[list[TeamMembership]] = relationship(
        "TeamMembership",
        back_populates="team",
        cascade="all, delete-orphan",
    )


class TeamMembership(Base, AutoUUIDMixin):
    """Join table: user ↔ team with per-membership role."""

    __tablename__ = "team_memberships"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
    )
    team_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("teams.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[TeamMemberRole] = mapped_column(
        Enum(TeamMemberRole),
        default=TeamMemberRole.MEMBER,
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_uuid", "team_uuid", name="uq_team_membership_user_team"),
    )

    team: Mapped[Team] = relationship("Team", back_populates="memberships")
    user: Mapped[User] = relationship("User", back_populates="team_memberships")
