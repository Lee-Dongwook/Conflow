"""Outbox subscriber registrations.

Import side-effect only: handlers register themselves via
`register_subscriber_handler` at module load. Imported once from
`main.py` lifespan before the worker loop starts.

Real subscribers (Comms → A2UI summarizer, HR onboarding cascade, etc.)
land alongside their owning domains. The debug handler below exists to
prove the dispatch loop end-to-end during Phase 1 alpha and is safe to
keep enabled in production (info-level log only).
"""

from __future__ import annotations

from .events import (
    COMMS_MENTION_CREATED,
    COMMS_MESSAGE_POSTED,
    PM_ISSUE_BLOCKED,
    PM_ISSUE_CANCELLED,
    PM_ISSUE_CREATED,
    PM_ISSUE_RESOLVED,
    PM_ISSUE_UNBLOCKED,
    PM_ISSUE_UPDATED,
)
from .outbox import EventEnvelope, register_subscriber_handler
from .runtime import logger

_DEBUG_EVENTS = (
    PM_ISSUE_CREATED,
    PM_ISSUE_UPDATED,
    PM_ISSUE_BLOCKED,
    PM_ISSUE_UNBLOCKED,
    PM_ISSUE_RESOLVED,
    PM_ISSUE_CANCELLED,
    COMMS_MESSAGE_POSTED,
    COMMS_MENTION_CREATED,
)


async def _debug_log_event(envelope: EventEnvelope) -> None:
    """Alpha-phase smoke handler. Logs the delivered event.

    Idempotent (pure log) so the at-least-once delivery semantics of the
    outbox worker are safe.
    """
    logger.info(
        "outbox event delivered: event=%s workspace=%s payload_keys=%s trace=%s",
        envelope.event_name,
        envelope.workspace_uuid,
        sorted(envelope.payload.keys()),
        envelope.trace_id,
    )


for _event_name in _DEBUG_EVENTS:
    register_subscriber_handler(_event_name, _debug_log_event)
