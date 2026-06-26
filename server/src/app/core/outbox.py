"""Outbox event dispatcher (Phase 1-2 transactional outbox pattern).

A background loop selects unpublished rows from `event_outbox`, hands each
to its registered subscribers, and stamps `published_at` on success.

`SELECT ... FOR UPDATE SKIP LOCKED` keeps multi-worker deployments safe:
when uvicorn runs with N workers, each polls a disjoint row set and no
event is delivered twice within a single cycle.

Phase 2 hardening (not yet in scope): exponential backoff, dead-letter
queue, dispatch-once guarantees per handler. Handlers MUST be idempotent
because a partial-delivery failure (one handler raises while others succeed)
leaves the row unpublished and the full handler chain is re-invoked on the
next cycle.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .runtime import logger
from .shared import EventOutbox


class EventEnvelope:
    """Read-only view of an outbox row handed to subscribers."""

    __slots__ = (
        "event_name",
        "occurred_at",
        "payload",
        "trace_id",
        "uuid",
        "workspace_uuid",
    )

    def __init__(self, row: EventOutbox) -> None:
        self.uuid: str = row.uuid
        self.workspace_uuid: str = row.workspace_uuid
        self.event_name: str = row.event_name
        self.payload: dict[str, Any] = dict(row.payload)
        self.occurred_at: datetime = row.occurred_at
        self.trace_id: str | None = row.trace_id


EventHandler = Callable[[EventEnvelope], Awaitable[None]]


_subscribers: dict[str, list[EventHandler]] = defaultdict(list)


def register_subscriber(event_name: str) -> Callable[[EventHandler], EventHandler]:
    """Decorator: register a handler for `event_name`. Handlers run in
    registration order; multiple handlers per event are supported.
    """

    def _decorator(fn: EventHandler) -> EventHandler:
        _subscribers[event_name].append(fn)
        return fn

    return _decorator


def register_subscriber_handler(event_name: str, handler: EventHandler) -> None:
    """Function-style alternative to the decorator."""
    _subscribers[event_name].append(handler)


def clear_subscribers() -> None:
    """For tests. Drops all handlers."""
    _subscribers.clear()


async def process_unpublished_batch(
    db: AsyncSession,
    *,
    limit: int = 100,
) -> int:
    """Process one batch. Returns the number of rows fully published.

    Rows whose handler chain raises are left with `published_at` NULL and
    retried on the next cycle.
    """
    res = await db.execute(
        select(EventOutbox)
        .where(EventOutbox.published_at.is_(None))
        .order_by(EventOutbox.occurred_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    rows = list(res.scalars().all())
    if not rows:
        return 0

    now = datetime.now(timezone.utc)  # noqa: UP017
    published = 0
    for row in rows:
        handlers = _subscribers.get(row.event_name, [])
        envelope = EventEnvelope(row)
        all_ok = True
        for handler in handlers:
            try:
                await handler(envelope)
            except Exception:
                handler_name = getattr(handler, "__name__", repr(handler))
                logger.exception(
                    "outbox subscriber failed: event=%s uuid=%s handler=%s",
                    row.event_name,
                    row.uuid,
                    handler_name,
                )
                all_ok = False
                # Keep running remaining handlers; the row stays unpublished
                # and the whole chain is retried next cycle. Handlers MUST
                # be idempotent.
        if all_ok:
            row.published_at = now
            published += 1
    await db.commit()
    return published


async def outbox_worker_loop(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    poll_interval_seconds: float = 1.0,
    batch_size: int = 100,
    stop_event: asyncio.Event | None = None,
) -> None:
    """Long-running poll loop. Cancels cleanly on task cancel or stop_event."""
    logger.info(
        "outbox worker started (interval=%.2fs, batch=%d)",
        poll_interval_seconds,
        batch_size,
    )
    try:
        while True:
            if stop_event is not None and stop_event.is_set():
                break
            try:
                async with session_factory() as db:
                    n = await process_unpublished_batch(db, limit=batch_size)
                    if n:
                        logger.debug("outbox worker published %d events", n)
            except Exception:
                logger.exception("outbox worker batch failed")
            try:
                await asyncio.sleep(poll_interval_seconds)
            except asyncio.CancelledError:
                break
    finally:
        logger.info("outbox worker stopped")
