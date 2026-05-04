from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from sqlalchemy import DateTime, Index, String, event, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, Session, mapped_column

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
