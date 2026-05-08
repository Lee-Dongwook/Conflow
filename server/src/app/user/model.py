from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base


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
    profile_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supabase_uuid: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    auth_id: Mapped[str | None] = mapped_column(String(500), nullable=True)

