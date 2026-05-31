from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..sprint.model import Sprint
    from ..team.model import Team
    from ..user.model import User


class BacklogPriority(enum.Enum):
    """PostgreSQL enum ``backlog_priority``; migration labels must match."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BacklogItem(Base, AutoUUIDMixin):
    """Backlog row scoped to one team and one sprint."""

    __tablename__ = "backlog_items"

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

    team_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("teams.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    sprint_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("sprints.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)

    assignee_user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
    )

    priority: Mapped[BacklogPriority] = mapped_column(
        Enum(
            BacklogPriority,
            name="backlog_priority",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)

    team: Mapped[Team] = relationship("Team", back_populates="backlog_items")
    sprint: Mapped[Sprint] = relationship("Sprint", back_populates="backlog_items")
    assignee: Mapped[User | None] = relationship(
        "User",
        back_populates="assigned_backlog_items",
        foreign_keys=[assignee_user_uuid],
    )
