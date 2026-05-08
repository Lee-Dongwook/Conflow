from __future__ import annotations

import uuid
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
    __tablename__ = "user"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda:str(uuid.uuid4()),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    name: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    profile_image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    supabase_uuid: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    auth_id: Mapped[str | None] = mapped_column(String(500), nullable=True)

