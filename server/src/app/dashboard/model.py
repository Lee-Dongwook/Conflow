from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..sprint.model import Sprint
    from ..team.model import Team


class DashboardConfig(Base, AutoUUIDMixin):
    """Per-sprint dashboard state: blocker notes, deadline labels, course context.

    1:1 with Sprint (unique constraint on sprint_uuid).
    """

    __tablename__ = "dashboard_configs"

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

    course_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    blocker_note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    next_deadline_label: Mapped[str | None] = mapped_column(String(256), nullable=True)

    __table_args__ = (
        UniqueConstraint("sprint_uuid", name="uq_dashboard_config_sprint"),
    )

    team: Mapped[Team] = relationship("Team", back_populates="dashboard_configs")
    sprint: Mapped[Sprint] = relationship("Sprint", back_populates="dashboard_config")
