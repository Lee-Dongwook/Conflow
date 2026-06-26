"""Event emission helper for the transactional outbox pattern.

Per docs/04-architecture/tech-stack.md "Event Bus 결정": Phase 1-2 writes
event rows to `event_outbox` in the same transaction as the domain
mutation. A worker (separate process, lands in a later step) polls the
unpublished partition and delivers to subscribers — other domains and the
A2UI Tool Registry.

Event names follow the catalog in docs/02-product/domain-overview.md.
Use the constants below; never inline a raw string at the call site.
"""

from __future__ import annotations

from typing import Any, Final

from sqlalchemy.ext.asyncio import AsyncSession

from .shared import EventOutbox

# --- Event name catalog (Phase 1 scope) ---

# PM
PM_ISSUE_CREATED: Final = "pm.issue.created"
PM_ISSUE_UPDATED: Final = "pm.issue.updated"
PM_ISSUE_BLOCKED: Final = "pm.issue.blocked"
PM_ISSUE_UNBLOCKED: Final = "pm.issue.unblocked"
PM_ISSUE_RESOLVED: Final = "pm.issue.resolved"
PM_ISSUE_CANCELLED: Final = "pm.issue.cancelled"

# Comms
COMMS_MESSAGE_POSTED: Final = "comms.message.posted"
COMMS_MENTION_CREATED: Final = "comms.mention.created"


def emit_event(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    event_name: str,
    payload: dict[str, Any] | None = None,
    trace_id: str | None = None,
) -> None:
    """Append an unpublished row to `event_outbox` in the current transaction.

    The caller still owns `commit()`. `published_at` stays NULL until the
    outbox worker delivers the event to all subscribers.
    """
    db.add(
        EventOutbox(
            workspace_uuid=workspace_uuid,
            event_name=event_name,
            payload=payload or {},
            trace_id=trace_id,
        )
    )
