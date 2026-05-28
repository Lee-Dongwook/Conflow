from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..backlog.model import BacklogItem
    from ..board.model import BoardCard
    from ..dashboard.model import DashboardConfig
    from ..retro.model import RetroBoard
    from ..team.model import Team
    from ..week.model import WeekMilestone


class Sprint(Base, AutoUUIDMixin):
    __tablename__ = "sprints"

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

    label: Mapped[str] = mapped_column(String(128), nullable=False)
    starts_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    ends_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    shared_goal: Mapped[str] = mapped_column(String(256), nullable=True)
    period_label: Mapped[str] = mapped_column(String(128), nullable=True)

    team: Mapped[Team] = relationship("Team", back_populates="sprints")
    sprint_metric_snapshots: Mapped[list[SprintMetricSnapshot]] = relationship(
        "SprintMetricSnapshot",
        back_populates="sprint",
        cascade="all, delete-orphan",
    )

    backlog_items: Mapped[list[BacklogItem]] = relationship(
        "BacklogItem",
        back_populates="sprint",
        passive_deletes=True,
    )

    board_cards: Mapped[list[BoardCard]] = relationship(
        "BoardCard",
        back_populates="sprint",
        passive_deletes=True,
    )

    retro_boards: Mapped[list[RetroBoard]] = relationship(
        "RetroBoard",
        back_populates="sprint",
        passive_deletes=True,
    )

    week_milestones: Mapped[list[WeekMilestone]] = relationship(
        "WeekMilestone",
        back_populates="sprint",
        passive_deletes=True,
    )

    dashboard_config: Mapped[DashboardConfig | None] = relationship(
        "DashboardConfig",
        back_populates="sprint",
        uselist=False,
        passive_deletes=True,
    )


class SprintMetricSnapshot(Base, AutoUUIDMixin):
    __tablename__ = "sprint_metric_snapshots"

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

    week_label: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    sprint: Mapped[Sprint] = relationship("Sprint", back_populates="sprint_metric_snapshots")
