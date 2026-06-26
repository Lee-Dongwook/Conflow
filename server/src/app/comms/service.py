"""Headless Comms service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments and returns Pydantic models — no React, no FastAPI
Depends (docs/04-architecture/a2ui-strategy.md).

Permission policy:
- Domain rules (edit window, DM archive ban, ChannelType invariants,
  author-only DM delete) are enforced inline.
- Role-based authorization (Member / Admin) is delegated to
  `core.permissions` — no role logic is inlined here (Watch List #2).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import (
    PermissionDenied,
    is_workspace_admin,
    require_workspace_admin,
    require_workspace_member,
    require_workspace_writer,
)
from ..core.shared import AuditDomain, AuditLog
from .model import Channel, ChannelMember, ChannelType, Message
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

# Slack-equivalent edit window. Author edits past this are rejected.
MESSAGE_EDIT_WINDOW = timedelta(hours=24)


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _audit(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    actor_member_uuid: str | None,
    action: str,
    resource_type: str,
    resource_uuid: str,
    metadata: dict | None = None,
) -> None:
    """Record a Comms mutation in the unified AuditLog. Caller owns commit."""
    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=actor_member_uuid,
            domain=AuditDomain.COMMS,
            action=action,
            resource_type=resource_type,
            resource_uuid=resource_uuid,
            audit_metadata=metadata or {},
        )
    )


async def _get_channel_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    channel_uuid: str,
) -> Channel:
    res = await db.execute(
        select(Channel).where(
            Channel.uuid == channel_uuid,
            Channel.workspace_uuid == workspace_uuid,
            Channel.deleted_at.is_(None),
        )
    )
    channel = res.scalar_one_or_none()
    if not channel:
        raise _not_found("Channel not found")
    return channel


async def _get_message_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    message_uuid: str,
) -> Message:
    res = await db.execute(
        select(Message).where(
            Message.uuid == message_uuid,
            Message.workspace_uuid == workspace_uuid,
            Message.deleted_at.is_(None),
        )
    )
    message = res.scalar_one_or_none()
    if not message:
        raise _not_found("Message not found")
    return message


async def _assert_active_member(
    db: AsyncSession,
    *,
    channel_uuid: str,
    member_uuid: str,
) -> ChannelMember:
    """Verify caller is a non-left member of the channel — required for
    posting, editing, joining-related, and reading inside private channels.
    """
    res = await db.execute(
        select(ChannelMember).where(
            ChannelMember.channel_uuid == channel_uuid,
            ChannelMember.member_uuid == member_uuid,
            ChannelMember.left_at.is_(None),
        )
    )
    cm = res.scalar_one_or_none()
    if not cm:
        raise _forbidden("Not a member of this channel")
    return cm


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------


async def create_channel(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: ChannelCreateInput,
    db: AsyncSession,
) -> ChannelReadOutput:
    # External channels host outside collaborators (e.g. 노무사) — Admin only.
    # DM channels go through a dedicated initiate_dm flow (not this entry point).
    if payload.type == ChannelType.EXTERNAL:
        await require_workspace_admin(
            db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
        )
    else:
        await require_workspace_writer(
            db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
        )
    if payload.type == ChannelType.DM:
        raise _bad_request("DM channels are created via initiate_dm, not create_channel")

    channel = Channel(
        workspace_uuid=workspace_uuid,
        name=payload.name,
        type=payload.type,
        topic=payload.topic,
        created_by_member_uuid=caller_member_uuid,
    )
    db.add(channel)
    await db.flush()

    # Creator + initial roster are added as members.
    roster = {caller_member_uuid, *payload.initial_member_uuids}
    for member_uuid in roster:
        db.add(
            ChannelMember(
                channel_uuid=channel.uuid,
                member_uuid=member_uuid,
                workspace_uuid=workspace_uuid,
            )
        )

    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.channel.created",
        resource_type="comms.channel",
        resource_uuid=channel.uuid,
        metadata={
            "name": channel.name,
            "type": channel.type.value,
            "initial_member_count": len(roster),
        },
    )
    await db.commit()
    await db.refresh(channel)
    return ChannelReadOutput.model_validate(channel)


async def list_channels(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: ChannelListFilter,
    db: AsyncSession,
) -> ChannelListOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    # Private/dm/external visibility is enforced by the JOIN when member_only
    # is True (default). With member_only=False only public channels remain
    # visible to non-members thanks to the channel-type filter below.
    base = select(Channel).where(
        Channel.workspace_uuid == workspace_uuid,
        Channel.deleted_at.is_(None),
    )
    if filters.type is not None:
        base = base.where(Channel.type == filters.type)
    if not filters.include_archived:
        base = base.where(Channel.is_archived.is_(False))
    if filters.member_only:
        base = base.join(
            ChannelMember,
            and_(
                ChannelMember.channel_uuid == Channel.uuid,
                ChannelMember.member_uuid == caller_member_uuid,
                ChannelMember.left_at.is_(None),
            ),
        )

    total_res = await db.execute(select(func.count()).select_from(base.subquery()))
    total = int(total_res.scalar_one())

    page_res = await db.execute(
        base.order_by(Channel.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    channels = [ChannelReadOutput.model_validate(c) for c in page_res.scalars().all()]
    return ChannelListOutput(channels=channels, total=total)


async def archive_channel(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    channel_uuid: str,
    db: AsyncSession,
) -> ChannelReadOutput:
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    channel = await _get_channel_or_404(
        db, workspace_uuid=workspace_uuid, channel_uuid=channel_uuid
    )
    if (
        channel.created_by_member_uuid != caller_member_uuid
        and not is_workspace_admin(roles)
    ):
        raise PermissionDenied("Channel creator or workspace Admin only")

    # Domain rule: DM and external channels are not archivable
    # (DM is membership-addressed; external follows collaborator lifecycle).
    if channel.type in {ChannelType.DM, ChannelType.EXTERNAL}:
        raise _bad_request(f"Cannot archive a {channel.type.value} channel")
    if channel.is_archived:
        return ChannelReadOutput.model_validate(channel)

    channel.is_archived = True
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.channel.archived",
        resource_type="comms.channel",
        resource_uuid=channel.uuid,
    )
    await db.commit()
    await db.refresh(channel)
    return ChannelReadOutput.model_validate(channel)


async def join_channel(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    channel_uuid: str,
    db: AsyncSession,
) -> None:
    # Self-join entry point — workspace membership required. The non-public
    # channel block below covers private/dm/external (those go through
    # invitation flows, not this function).
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    channel = await _get_channel_or_404(
        db, workspace_uuid=workspace_uuid, channel_uuid=channel_uuid
    )
    if channel.is_archived:
        raise _bad_request("Cannot join an archived channel")
    if channel.type != ChannelType.PUBLIC:
        # Non-public joins go through invitation flow (not this entry point).
        raise _forbidden(f"{channel.type.value} channels require invitation")

    existing = await db.execute(
        select(ChannelMember).where(
            ChannelMember.channel_uuid == channel_uuid,
            ChannelMember.member_uuid == caller_member_uuid,
        )
    )
    cm = existing.scalar_one_or_none()
    if cm and cm.left_at is None:
        return  # idempotent
    if cm:
        cm.left_at = None
        cm.joined_at = datetime.now(timezone.utc)  # noqa: UP017
    else:
        db.add(
            ChannelMember(
                channel_uuid=channel_uuid,
                member_uuid=caller_member_uuid,
                workspace_uuid=workspace_uuid,
            )
        )
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.member.joined_channel",
        resource_type="comms.channel",
        resource_uuid=channel_uuid,
    )
    await db.commit()


async def leave_channel(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    channel_uuid: str,
    db: AsyncSession,
) -> None:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    channel = await _get_channel_or_404(
        db, workspace_uuid=workspace_uuid, channel_uuid=channel_uuid
    )
    # Domain rule: leaving a DM tears the conversation; force-leave is not a thing.
    if channel.type == ChannelType.DM:
        raise _bad_request("Cannot leave a DM channel")

    res = await db.execute(
        select(ChannelMember).where(
            ChannelMember.channel_uuid == channel_uuid,
            ChannelMember.member_uuid == caller_member_uuid,
            ChannelMember.left_at.is_(None),
        )
    )
    cm = res.scalar_one_or_none()
    if not cm:
        return  # idempotent
    cm.left_at = datetime.now(timezone.utc)  # noqa: UP017
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.member.left_channel",
        resource_type="comms.channel",
        resource_uuid=channel_uuid,
    )
    await db.commit()


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


async def post_message(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: MessagePostInput,
    db: AsyncSession,
) -> MessageReadOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    channel = await _get_channel_or_404(
        db, workspace_uuid=workspace_uuid, channel_uuid=payload.channel_uuid
    )
    if channel.is_archived:
        raise _bad_request("Cannot post to an archived channel")

    # Posting requires active membership in the channel.
    await _assert_active_member(
        db, channel_uuid=channel.uuid, member_uuid=caller_member_uuid
    )

    # Thread sanity: root must exist in the same channel.
    if payload.thread_root_uuid is not None:
        root = await _get_message_or_404(
            db, workspace_uuid=workspace_uuid, message_uuid=payload.thread_root_uuid
        )
        if root.channel_uuid != channel.uuid:
            raise _bad_request("thread_root_uuid is not in this channel")

    message = Message(
        workspace_uuid=workspace_uuid,
        channel_uuid=channel.uuid,
        thread_root_uuid=payload.thread_root_uuid,
        author_member_uuid=caller_member_uuid,
        body=payload.body,
        mentions=payload.mentions,
        attachments=payload.attachments,
    )
    db.add(message)
    await db.flush()

    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.message.posted",
        resource_type="comms.message",
        resource_uuid=message.uuid,
        metadata={
            "channel_uuid": channel.uuid,
            "thread_root_uuid": payload.thread_root_uuid,
            "mention_count": len(payload.mentions),
            "attachment_count": len(payload.attachments),
        },
    )
    if payload.mentions:
        _audit(
            db,
            workspace_uuid=workspace_uuid,
            actor_member_uuid=caller_member_uuid,
            action="comms.mention.created",
            resource_type="comms.message",
            resource_uuid=message.uuid,
            metadata={"mentioned_member_uuids": payload.mentions},
        )

    await db.commit()
    await db.refresh(message)
    return MessageReadOutput.model_validate(message)


async def list_messages_in_channel(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: MessageListFilter,
    db: AsyncSession,
) -> MessageListOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    channel = await _get_channel_or_404(
        db, workspace_uuid=workspace_uuid, channel_uuid=filters.channel_uuid
    )

    # Public channels are readable workspace-wide;
    # private/dm/external require active membership.
    if channel.type != ChannelType.PUBLIC:
        await _assert_active_member(
            db, channel_uuid=channel.uuid, member_uuid=caller_member_uuid
        )

    base = select(Message).where(
        Message.workspace_uuid == workspace_uuid,
        Message.channel_uuid == channel.uuid,
        Message.deleted_at.is_(None),
    )
    if filters.thread_root_uuid is not None:
        base = base.where(Message.thread_root_uuid == filters.thread_root_uuid)
    else:
        # Default: top-level only (no thread replies).
        base = base.where(Message.thread_root_uuid.is_(None))
    if filters.before is not None:
        base = base.where(Message.created_at < filters.before)
    if filters.after is not None:
        base = base.where(Message.created_at > filters.after)

    res = await db.execute(
        base.order_by(Message.created_at.desc()).limit(filters.limit + 1)
    )
    rows = list(res.scalars().all())
    has_more = len(rows) > filters.limit
    page = rows[: filters.limit]
    return MessageListOutput(
        messages=[MessageReadOutput.model_validate(m) for m in page],
        has_more=has_more,
    )


async def edit_message(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    message_uuid: str,
    payload: MessageUpdateInput,
    db: AsyncSession,
) -> MessageReadOutput:
    # Disabled / external-only callers are filtered here even though the
    # author check below would also reject them.
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    message = await _get_message_or_404(
        db, workspace_uuid=workspace_uuid, message_uuid=message_uuid
    )

    # Domain rule (immediately enforced): author only, no Admin bypass even in DMs.
    if message.author_member_uuid != caller_member_uuid:
        raise _forbidden("Only the author may edit this message")

    now = datetime.now(timezone.utc)  # noqa: UP017
    if (now - message.created_at) > MESSAGE_EDIT_WINDOW:
        raise _bad_request("Edit window expired (24h)")

    message.body = payload.body
    message.edited_at = now
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.message.edited",
        resource_type="comms.message",
        resource_uuid=message.uuid,
    )
    await db.commit()
    await db.refresh(message)
    return MessageReadOutput.model_validate(message)


async def delete_message(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    message_uuid: str,
    db: AsyncSession,
) -> None:
    message = await _get_message_or_404(
        db, workspace_uuid=workspace_uuid, message_uuid=message_uuid
    )
    channel = await _get_channel_or_404(
        db, workspace_uuid=workspace_uuid, channel_uuid=message.channel_uuid
    )

    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    # Domain rule: in DM channels, even Admin cannot delete — only the author.
    is_author = message.author_member_uuid == caller_member_uuid
    if channel.type == ChannelType.DM and not is_author:
        raise _forbidden("DM messages are deletable only by the author")
    # Outside DM: author or workspace Admin.
    if not is_author and not is_workspace_admin(roles):
        raise _forbidden("Only the author or workspace Admin may delete")

    message.deleted_at = datetime.now(timezone.utc)  # noqa: UP017
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="comms.message.deleted",
        resource_type="comms.message",
        resource_uuid=message.uuid,
        metadata={"channel_type": channel.type.value},
    )
    await db.commit()
