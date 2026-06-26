"""Outbox subscriber registrations.

Import side-effect only: handlers register themselves via
`register_subscriber_handler` at module load. Imported once from
`main.py` lifespan before the worker loop starts.

Mix of debug-log handlers (kept everywhere for observability) and real
cross-domain handlers (first one: `documents.contract.signed` →
`EmployeeProfile.contract_signed_at`).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import update

from .events import (
    COMMS_MENTION_CREATED,
    COMMS_MESSAGE_POSTED,
    DOCUMENTS_CONTRACT_SIGNED,
    DOCUMENTS_INSTANCE_ISSUED,
    DOCUMENTS_INSTANCE_VOIDED,
    HR_LEAVE_APPROVED,
    HR_LEAVE_REJECTED,
    HR_LEAVE_SUBMITTED,
    HR_MEMBER_OFFBOARDED,
    HR_MEMBER_ONBOARDED,
    HR_ONE_ON_ONE_RECORDED,
    HR_PROFILE_UPDATED,
    PM_ISSUE_BLOCKED,
    PM_ISSUE_CANCELLED,
    PM_ISSUE_CREATED,
    PM_ISSUE_RESOLVED,
    PM_ISSUE_UNBLOCKED,
    PM_ISSUE_UPDATED,
    WORKSPACE_MEMBER_INVITED,
    WORKSPACE_MEMBER_JOINED,
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
    HR_MEMBER_ONBOARDED,
    HR_MEMBER_OFFBOARDED,
    HR_PROFILE_UPDATED,
    HR_LEAVE_SUBMITTED,
    HR_LEAVE_APPROVED,
    HR_LEAVE_REJECTED,
    HR_ONE_ON_ONE_RECORDED,
    WORKSPACE_MEMBER_INVITED,
    WORKSPACE_MEMBER_JOINED,
    DOCUMENTS_INSTANCE_ISSUED,
    DOCUMENTS_CONTRACT_SIGNED,
    DOCUMENTS_INSTANCE_VOIDED,
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


async def _handle_contract_signed(envelope: EventEnvelope) -> None:
    """`documents.contract.signed` → stamp `EmployeeProfile.contract_signed_at`.

    Idempotent: the `UPDATE ... WHERE contract_signed_at IS NULL OR <`
    guard means at-least-once delivery never moves the timestamp backwards.
    A no-op (rowcount=0) when the subject isn't in HR yet is logged but
    not retried — the contract may simply belong to a non-employee.
    """
    # Local import: outbox_subscribers loads before the application is
    # fully wired, so deferring DB access keeps the import cheap.
    from src.app.core.database import async_session  # noqa: PLC0415
    from src.app.hr.model import EmployeeProfile  # noqa: PLC0415

    if async_session is None:
        logger.warning("contract.signed: async_session not ready, skipping")
        return

    subject_member_uuid = envelope.payload.get("subject_member_uuid")
    issued_at_iso = envelope.payload.get("issued_at")
    if not subject_member_uuid or not issued_at_iso:
        logger.warning(
            "contract.signed: missing subject_member_uuid or issued_at "
            "(envelope_uuid=%s)",
            envelope.uuid,
        )
        return

    try:
        issued_at = datetime.fromisoformat(issued_at_iso)
    except ValueError:
        logger.warning(
            "contract.signed: malformed issued_at=%s (envelope_uuid=%s)",
            issued_at_iso,
            envelope.uuid,
        )
        return

    # Subscribers run in their own session, so the per-workspace RLS
    # context must be re-established here (the worker batch's system_mode
    # only applies to the batch select, not to handler sessions).
    from .db_context import set_workspace_context  # noqa: PLC0415

    async with async_session() as db:
        await set_workspace_context(db, workspace_uuid=envelope.workspace_uuid)
        result = await db.execute(
            update(EmployeeProfile)
            .where(
                EmployeeProfile.workspace_uuid == envelope.workspace_uuid,
                EmployeeProfile.member_uuid == subject_member_uuid,
                EmployeeProfile.deleted_at.is_(None),
            )
            .values(contract_signed_at=issued_at)
        )
        await db.commit()
        if result.rowcount == 0:
            logger.info(
                "contract.signed: no EmployeeProfile for member=%s "
                "in workspace=%s (subject may not be an employee)",
                subject_member_uuid,
                envelope.workspace_uuid,
            )
        else:
            logger.info(
                "contract.signed: stamped contract_signed_at on EmployeeProfile "
                "for member=%s (workspace=%s)",
                subject_member_uuid,
                envelope.workspace_uuid,
            )


register_subscriber_handler(DOCUMENTS_CONTRACT_SIGNED, _handle_contract_signed)
