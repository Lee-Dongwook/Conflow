from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class WorkspaceTier(enum.Enum):
    FREE = "free"
    TEAM = "team"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class WorkspaceRegion(enum.Enum):
    KR = "kr"
    JP = "jp"


class Workspace(Base, AutoUUIDMixin):
    __tablename__ = "workspaces"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    tier: Mapped[WorkspaceTier] = mapped_column(
        Enum(
            WorkspaceTier,
            name="workspace_tier",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=WorkspaceTier.FREE,
        nullable=False,
    )

    region: Mapped[WorkspaceRegion] = mapped_column(
        Enum(
            WorkspaceRegion,
            name="workspace_region",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=WorkspaceRegion.KR,
        nullable=False,
    )

    billing_account_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
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

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_workspaces_slug", "slug"),
        Index("idx_workspaces_tier", "tier"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
