"""Comms domain Tools — register at import."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ....comms.schemas import (
    MessageListFilter,
    MessageListOutput,
)
from ....comms.service import list_messages_in_channel
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
