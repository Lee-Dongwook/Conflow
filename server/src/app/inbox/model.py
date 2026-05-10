from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..user.model import User


class InboxEntry(Base, AutoUUIDMixin):
    """User inbox row; team/sprint are not modeled (see domain doc). Multiple user FKs by role."""

    __tablename__ = "inbox_entries"

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

    recipient_user_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
    )
    sender_user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str | None] = mapped_column(Text(), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)

    recipient: Mapped[User] = relationship(
        "User",
        back_populates="received_inbox_entries",
        foreign_keys=[recipient_user_uuid],
    )
    sender: Mapped[User | None] = relationship(
        "User",
        back_populates="sent_inbox_entries",
        foreign_keys=[sender_user_uuid],
    )
