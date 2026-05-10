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
    from ..user.model import User


class RetroBoard(Base, AutoUUIDMixin):
    """Retro board anchored to a sprint."""

    __tablename__ = "retro_boards"

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

    title: Mapped[str | None] = mapped_column(String(256), nullable=True)

    sprint: Mapped[Sprint] = relationship("Sprint", back_populates="retro_boards")
    columns: Mapped[list[RetroColumn]] = relationship(
        "RetroColumn",
        back_populates="retro_board",
        cascade="all, delete-orphan",
        order_by="RetroColumn.sort_order",
    )


class RetroColumn(Base, AutoUUIDMixin):
    """KPT-style column on a retro board."""

    __tablename__ = "retro_columns"

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

    retro_board_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("retro_boards.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(String(128), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)

    retro_board: Mapped[RetroBoard] = relationship("RetroBoard", back_populates="columns")
    items: Mapped[list[RetroItem]] = relationship(
        "RetroItem",
        back_populates="retro_column",
        cascade="all, delete-orphan",
    )


class RetroItem(Base, AutoUUIDMixin):
    """Single sticky/card line in a retro column."""

    __tablename__ = "retro_items"

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

    retro_column_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("retro_columns.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    body: Mapped[str] = mapped_column(Text(), nullable=False)

    author_user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
    )

    retro_column: Mapped[RetroColumn] = relationship("RetroColumn", back_populates="items")
    author: Mapped[User | None] = relationship(
        "User",
        back_populates="authored_retro_items",
        foreign_keys=[author_user_uuid],
    )
