from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..sprint.model import Sprint
    from ..user.model import User


class WeekMilestone(Base, AutoUUIDMixin):
    """This-week milestone row tied to a sprint and an owning user."""

    __tablename__ = "week_milestones"

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

    sprint_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("sprints.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    owner_user_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    due_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    sprint: Mapped[Sprint] = relationship("Sprint", back_populates="week_milestones")
    owner: Mapped[User] = relationship(
        "User",
        back_populates="owned_week_milestones",
        foreign_keys=[owner_user_uuid],
    )
