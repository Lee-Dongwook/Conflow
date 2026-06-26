"""Pydantic Input / Output schemas for Comms service functions.

Per docs/04-architecture/a2ui-strategy.md "Schema-first": every service
function exposes Pydantic schemas so it can be lifted into the A2UI Tool
Registry without rework.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .model import ChannelType

# -- Channel --


class ChannelCreateInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: ChannelType
    topic: str | None = None
    # Optional initial roster (creator is always added).
    initial_member_uuids: list[str] = Field(default_factory=list)


class ChannelReadOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    name: str
    type: ChannelType
    topic: str | None
    is_archived: bool
    created_by_member_uuid: str
    created_at: datetime
    updated_at: datetime


class ChannelListFilter(BaseModel):
    type: ChannelType | None = None
    include_archived: bool = False
    # When True, only channels the caller is a member of.
    member_only: bool = True
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class ChannelListOutput(BaseModel):
    channels: list[ChannelReadOutput]
    total: int


# -- Message --


class MessagePostInput(BaseModel):
    channel_uuid: str
    body: str = Field(min_length=1)
    thread_root_uuid: str | None = None
    mentions: list[str] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class MessageUpdateInput(BaseModel):
    body: str = Field(min_length=1)


class MessageReadOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    channel_uuid: str
    thread_root_uuid: str | None
    author_member_uuid: str
    body: str
    attachments: list[dict[str, Any]]
    mentions: list[str]
    created_at: datetime
    edited_at: datetime | None


class MessageListFilter(BaseModel):
    channel_uuid: str
    thread_root_uuid: str | None = None
    # Cursor-style window (DESC by created_at).
    before: datetime | None = None
    after: datetime | None = None
    limit: int = Field(default=50, ge=1, le=200)


class MessageListOutput(BaseModel):
    messages: list[MessageReadOutput]
    has_more: bool
