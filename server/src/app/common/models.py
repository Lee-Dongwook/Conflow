from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from sqlalchemy import DateTime, Index, event, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


@runtime_checkable
class IdGeneratorProtocol(Protocol):
    def generate(self) -> str: ...

class UUIDv4Generator:
    def generate(self) -> str:
        import uuid as _uuid
        return str(_uuid.uuid4())

class UUIDv7Generator:
    def generate(self) -> str:
        from .id import uuid7
        return str(uuid7())

_uuid_generator: IdGeneratorProtocol = UUIDv4Generator() if os.getenv("UUID_VERSION", "7") == "4" else UUIDv7Generator()  # noqa: E501

class AutoUUIDMixin:
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        @event.listens_for(cls, "init")
        def _auto_uuid(target: AutoUUIDMixin, args: tuple, kwargs: dict) -> None: # type: ignore[type-arg]
            if not kwargs.get("uuid"):
                kwargs["uuid"] = _uuid_generator.generate()


class CommonResource(Base):
    __tablename__ = "common_resources"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
    )

    user_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        Index("idx_common_resources_user_uuid", "user_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class ResourceRegistry:
    def generate(self) -> str:
        return _uuid_generator.generate()
    
    async def soft_delete(self, db: AsyncSession, uuid: str) -> None:
        await db.execute(
            update(CommonResource).where(CommonResource.uuid == uuid)
            .values(deleted_at=datetime.now(timezone.utc))
        )


resource_registry = ResourceRegistry()
