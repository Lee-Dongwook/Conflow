from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class EventOutbox(Base, AutoUUIDMixin):
    """Transactional outbox for domain events (Phase 1-2 event bus).

    Per docs/04-architecture/tech-stack.md "Event Bus 결정":
    - Phase 1-2: rows inserted in the same transaction as the domain mutation.
      A worker polls (or LISTEN/NOTIFY-listens on) `published_at IS NULL`,
      delivers to subscribers, then stamps `published_at`.
    - Phase 3+: same rows are dual-written to Kafka during the 6-week
      migration window; this table becomes the durable backup.

    `event_name` follows the catalog in docs/02-product/domain-overview.md
    (e.g. `pm.issue.created`, `comms.message.posted`).
    """

    __tablename__ = "event_outbox"

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

    event_name: Mapped[str] = mapped_column(String(80), nullable=False)

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    # NULL until a worker delivers to all subscribers and stamps the time.
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Number of full handler-chain attempts that have failed. The worker
    # bumps this on each failure; once it crosses `MAX_RETRIES` (in
    # `core/outbox.py`), `dead_at` is stamped and the row drops out of
    # the unpublished partition.
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )

    # Exponential backoff. The worker filters `next_attempt_at <= NOW()` so
    # a failed row is invisible until its delay elapses.
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Stamped when retries exhaust. Together with `published_at` this gives
    # the lifecycle: pending → published OR pending → dead.
    dead_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # OpenTelemetry trace id (32-char hex). Nullable until tracing rolls out.
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        # Hot path: worker polls "next unpublished (and not dead), eligible
        # now, oldest first". Partial index keeps it tiny.
        Index(
            "idx_event_outbox_unpublished",
            "occurred_at",
            postgresql_where=text("published_at IS NULL AND dead_at IS NULL"),
        ),
        # Dead-letter inspection — small, but very hot when triaging incidents.
        Index(
            "idx_event_outbox_dead",
            "dead_at",
            postgresql_where=text("dead_at IS NOT NULL"),
        ),
        # Per-workspace event timeline / replay.
        Index(
            "idx_event_outbox_workspace_event_occurred",
            "workspace_uuid",
            "event_name",
            "occurred_at",
        ),
    )

    @property
    def is_published(self) -> bool:
        return self.published_at is not None

    @property
    def is_dead(self) -> bool:
        return self.dead_at is not None
