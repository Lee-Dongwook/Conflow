from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base


class Agent(Base, AutoUUIDMixin):
    __tablename__ = "agent"
    __registry_type__ = "agent"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
    )
    name: Mapped[str] = mapped_column(
        String,
    )
    slug: Mapped[str] = mapped_column(
        String,
        unique=True,
    )
    description: Mapped[str] = mapped_column(String, default="")
