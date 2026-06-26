"""Comms domain Tools — register at import."""

from __future__ import annotations

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....comms.model import Message
from ....comms.schemas import (
    MessageListFilter,
    MessageListOutput,
)
from ....comms.service import list_messages_in_channel
from ....pm.schemas import IssueCreateInput, IssuePriority, IssueReadOutput
from ....pm.service import create_issue
from ...shared import WorkspaceTier
from ..registry import PermissionLevel, ToolSpec, register_tool


async def _comms_search_messages(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: MessageListFilter,
    db: AsyncSession,
) -> MessageListOutput:
    return await list_messages_in_channel(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        filters=payload,
        db=db,
    )


register_tool(
    ToolSpec(
        id="comms.search_messages",
        domain="comms",
        description=(
            "List messages in a channel with optional thread / time-window "
            "filter. Returns top-level messages only when thread_root is unset."
        ),
        handler=_comms_search_messages,
        input_schema=MessageListFilter,
        output_schema=MessageListOutput,
        min_tier=WorkspaceTier.FREE,
        permission_required=PermissionLevel.MEMBER,
        phase=1,
    )
)


# ---------------------------------------------------------------------------
# comms.message_to_issue — promote a Comms message to a PM Issue (cross-domain)
# ---------------------------------------------------------------------------


class CommsMessageToIssueInput(BaseModel):
    message_uuid: str
    title_override: str | None = Field(
        default=None,
        max_length=200,
        description="Override the auto-derived title (first 100 chars of the message body).",
    )
    assignee_member_uuid: str | None = None
    priority: IssuePriority = IssuePriority.MEDIUM


async def _comms_message_to_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: CommsMessageToIssueInput,
    db: AsyncSession,
) -> IssueReadOutput:
    res = await db.execute(
        select(Message).where(
            Message.uuid == payload.message_uuid,
            Message.workspace_uuid == workspace_uuid,
            Message.deleted_at.is_(None),
        )
    )
    msg = res.scalar_one_or_none()
    if msg is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    title = payload.title_override or msg.body[:100].strip() or "Untitled"
    description = (
        f"Promoted from Comms message {msg.uuid} by member {caller_member_uuid}.\n\n"
        f"---\n{msg.body}"
    )

    return await create_issue(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        payload=IssueCreateInput(
            title=title,
            description=description,
            priority=payload.priority,
            assignee_member_uuid=payload.assignee_member_uuid,
        ),
        db=db,
    )


register_tool(
    ToolSpec(
        id="comms.message_to_issue",
        domain="comms",
        description=(
            "Promote a Comms message into a PM Issue. Title defaults to the "
            "first 100 chars of the message body; description preserves a "
            "link back to the original message."
        ),
        handler=_comms_message_to_issue,
        input_schema=CommsMessageToIssueInput,
        output_schema=IssueReadOutput,
        min_tier=WorkspaceTier.TEAM,
        permission_required=PermissionLevel.WRITER,
        cross_domain=True,
        phase=1,
    )
)
