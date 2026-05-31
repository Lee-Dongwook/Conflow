from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..backlog.model import BacklogItem
    from ..board.model import BoardCard
    from ..consent.model import UserConsent
    from ..retro.model import RetroItem
    from ..team.model import TeamMembership
    from ..week.model import WeekMilestone


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base, AutoUUIDMixin):
    """User domain model for account identity and profile data."""

    __tablename__ = "users"

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

    name: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole", values_callable=lambda e: [m.value for m in e]),
        default=UserRole.USER,
    )
    profile_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supabase_uuid: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    auth_id: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user_profile: Mapped[UserProfile | None] = relationship(
        "UserProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    team_memberships: Mapped[list[TeamMembership]] = relationship(
        "TeamMembership",
        back_populates="user",
    )

    assigned_backlog_items: Mapped[list[BacklogItem]] = relationship(
        "BacklogItem",
        back_populates="assignee",
        foreign_keys="BacklogItem.assignee_user_uuid",
    )

    assigned_board_cards: Mapped[list[BoardCard]] = relationship(
        "BoardCard",
        back_populates="assignee",
        foreign_keys="BoardCard.assignee_user_uuid",
    )

    reported_board_cards: Mapped[list[BoardCard]] = relationship(
        "BoardCard",
        back_populates="reporter",
        foreign_keys="BoardCard.reporter_user_uuid",
    )

    authored_retro_items: Mapped[list[RetroItem]] = relationship(
        "RetroItem",
        back_populates="author",
        foreign_keys="RetroItem.author_user_uuid",
    )

    owned_week_milestones: Mapped[list[WeekMilestone]] = relationship(
        "WeekMilestone",
        back_populates="owner",
        foreign_keys="WeekMilestone.owner_user_uuid",
    )

    consents: Mapped[list[UserConsent]] = relationship(
        "UserConsent",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("auth_id", name="uq_user_auth_id"),)


class UserProfile(Base):
    """Extended profile fields (1:1 with User)."""

    __tablename__ = "user_profiles"

    user_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid"),
        primary_key=True,
    )
    job_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locale: Mapped[str | None] = mapped_column(String(100), nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="user_profile")
