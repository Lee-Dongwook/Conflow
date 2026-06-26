from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class EntityLinkKind(enum.Enum):
    REFERENCES = "references"
    DERIVED_FROM = "derived_from"
    BLOCKS = "blocks"
    MENTIONED_IN = "mentioned_in"


class EntityLink(Base, AutoUUIDMixin):
    """Cross-domain references — the only legal way to link entities across
    PM / Comms / HR / Documents.

    Direct foreign keys between domain tables are forbidden (Watch List #1
    in docs/02-product/domain-overview.md). Permission checks must verify
    both source and target visibility — "편도 가시성 보장".

    Near-immutable: links are created or removed, never edited. `deleted_at`
    is the only mutable column.
    """

    __tablename__ = "entity_links"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    link_kind: Mapped[EntityLinkKind] = mapped_column(
        Enum(
            EntityLinkKind,
            name="entity_link_kind",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    created_by_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        # Forward lookup: "what does X point to?"
        Index(
            "idx_entity_links_source",
            "workspace_uuid",
            "source_type",
            "source_uuid",
        ),
        # Reverse lookup: "what points to Y with this link kind?"
        Index(
            "idx_entity_links_target_kind",
            "workspace_uuid",
            "target_type",
            "target_uuid",
            "link_kind",
        ),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
