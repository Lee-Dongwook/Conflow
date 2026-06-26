"""Comms HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.deps import get_caller_member
from ..core.shared import Member
from .schemas import (
    ChannelCreateInput,
    ChannelListFilter,
    ChannelListOutput,
    ChannelReadOutput,
    MessageListFilter,
    MessageListOutput,
    MessagePostInput,
    MessageReadOutput,
    MessageUpdateInput,
)
from .service import (
    archive_channel,
    create_channel,
    delete_message,
    edit_message,
    join_channel,
    leave_channel,
    list_channels,
    list_messages_in_channel,
    post_message,
)

router = APIRouter(prefix="/workspaces/{workspace_uuid}", tags=["comms"])


# ---------------------------------------------------------------------------
# Channel routes
# ---------------------------------------------------------------------------


@router.post(
    "/channels",
    response_model=ChannelReadOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel_endpoint(
    payload: ChannelCreateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> ChannelReadOutput:
    return await create_channel(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/channels", response_model=ChannelListOutput)
async def list_channels_endpoint(
    workspace_uuid: str = Path(...),
    filters: ChannelListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> ChannelListOutput:
    return await list_channels(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.post("/channels/{channel_uuid}/archive", response_model=ChannelReadOutput)
async def archive_channel_endpoint(
    channel_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> ChannelReadOutput:
    return await archive_channel(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        channel_uuid=channel_uuid,
        db=db,
    )


@router.post(
    "/channels/{channel_uuid}/join",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def join_channel_endpoint(
    channel_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    await join_channel(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        channel_uuid=channel_uuid,
        db=db,
    )


@router.post(
    "/channels/{channel_uuid}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def leave_channel_endpoint(
    channel_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    await leave_channel(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        channel_uuid=channel_uuid,
        db=db,
    )


# ---------------------------------------------------------------------------
# Message routes
# ---------------------------------------------------------------------------


@router.post(
    "/messages",
    response_model=MessageReadOutput,
    status_code=status.HTTP_201_CREATED,
)
async def post_message_endpoint(
    payload: MessagePostInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> MessageReadOutput:
    return await post_message(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/messages", response_model=MessageListOutput)
async def list_messages_endpoint(
    workspace_uuid: str = Path(...),
    filters: MessageListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> MessageListOutput:
    return await list_messages_in_channel(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.patch("/messages/{message_uuid}", response_model=MessageReadOutput)
async def edit_message_endpoint(
    message_uuid: str,
    payload: MessageUpdateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> MessageReadOutput:
    return await edit_message(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        message_uuid=message_uuid,
        payload=payload,
        db=db,
    )


@router.delete(
    "/messages/{message_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_message_endpoint(
    message_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    await delete_message(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        message_uuid=message_uuid,
        db=db,
    )
