from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base


class ChannelType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    DM = "dm"
    EXTERNAL = "external"  # 외부 협업자(노무사 등) 전용


class Channel(Base, AutoUUIDMixin):
    """A conversation container — the Comms domain's core aggregate.

    `name` is unique per workspace only for public/private channels; DM and
    external channels are addressed by membership, not name.
    """

    __tablename__ = "channels"

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

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    type: Mapped[ChannelType] = mapped_column(
        Enum(
            ChannelType,
            name="channel_type",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    topic: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        # Partial unique: only public/private channels collide on name.
        # DM/external channels are membership-addressed, so duplicate names are fine.
        Index(
            "uq_channels_workspace_name",
            "workspace_uuid",
            "name",
            unique=True,
            postgresql_where=text("type IN ('public', 'private')"),
        ),
        Index("idx_channels_workspace_type", "workspace_uuid", "type"),
        Index("idx_channels_created_by", "created_by_member_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class ChannelMember(Base):
    """M:N between Channel and Member. Composite PK, no AutoUUIDMixin.

    `workspace_uuid` is denormalized so RLS can filter without joining
    `channels`. `last_read_message_uuid` tracks unread counts on the client.
    """

    __tablename__ = "channel_members"

    channel_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("channels.uuid", ondelete="CASCADE"),
        primary_key=True,
    )

    member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        primary_key=True,
    )

    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    # NULL while active; set when the member leaves the channel.
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_read_message_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "idx_channel_members_workspace_member",
            "workspace_uuid",
            "member_uuid",
        ),
        # Active-membership lookup ("which channels is this member in?"):
        # partial so left memberships don't bloat the hot index.
        Index(
            "idx_channel_members_workspace_channel_active",
            "workspace_uuid",
            "channel_uuid",
            postgresql_where=text("left_at IS NULL"),
        ),
    )


class Message(Base, AutoUUIDMixin):
    """A single utterance — the decision-emergence point of the platform.

    `mentions` is a PostgreSQL `UUID[]` so a GIN index can resolve
    `@member` lookups without a join. `thread_root_uuid` is a self-FK;
    NULL on the thread root itself, set to root id on replies.
    """

    __tablename__ = "messages"

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

    channel_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("channels.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    thread_root_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("messages.uuid"),
        nullable=True,
    )

    author_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)

    # File attachment metadata: [{"uri": ..., "mime": ..., "size": ...}, ...]
    attachments: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )

    # Member UUIDs mentioned with @. GIN-indexed for fast reverse lookup.
    mentions: Mapped[list[str]] = mapped_column(
        ARRAY(UUID(as_uuid=False)),
        default=list,
        nullable=False,
        server_default=text("'{}'::uuid[]"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Soft delete. Hard-delete cadence is governed by Tier retention.
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        # Channel timeline (hot path)
        Index(
            "idx_messages_workspace_channel_created",
            "workspace_uuid",
            "channel_uuid",
            "created_at",
        ),
        # Thread replies
        Index(
            "idx_messages_workspace_thread",
            "workspace_uuid",
            "thread_root_uuid",
            "created_at",
        ),
        # Author timeline
        Index(
            "idx_messages_workspace_author_created",
            "workspace_uuid",
            "author_member_uuid",
            "created_at",
        ),
        # Reverse mention lookup
        Index("idx_messages_mentions", "mentions", postgresql_using="gin"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_thread_reply(self) -> bool:
        return self.thread_root_uuid is not None
