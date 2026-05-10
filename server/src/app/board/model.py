from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..sprint.model import Sprint
    from ..team.model import Team
    from ..user.model import User


class BoardCard(Base, AutoUUIDMixin):
    """Kanban card scoped to one team and one sprint; optional assignee and reporter users."""

    __tablename__ = "board_cards"

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
    column_key: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    position: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)

    assignee_user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
    )
    reporter_user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
    )

    team: Mapped[Team] = relationship("Team", back_populates="board_cards")
    sprint: Mapped[Sprint] = relationship("Sprint", back_populates="board_cards")
    assignee: Mapped[User | None] = relationship(
        "User",
        back_populates="assigned_board_cards",
        foreign_keys=[assignee_user_uuid],
    )
    reporter: Mapped[User | None] = relationship(
        "User",
        back_populates="reported_board_cards",
        foreign_keys=[reporter_user_uuid],
    )
