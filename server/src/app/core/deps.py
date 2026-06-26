"""Cross-domain FastAPI dependencies.

`get_caller_member` resolves the authenticated user's Member row in the
workspace identified by the URL path. PM/Comms/HR/Documents endpoints
take `caller_member: Member = Depends(get_caller_member)` and pass
`caller_member.uuid` into the service layer — service signatures stay
headless (no Request/Depends knowledge).

This dep also sets the per-transaction RLS context vars
(`app.workspace_uuid` and `app.member_uuid`) so the manually-applied
RLS policies in `alembic/manual_sql/rls_policies.sql` filter rows for
this request. The SET LOCAL is harmless when RLS isn't enabled.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.schemas import UserRead
from .database import get_async_db
from .db_context import set_workspace_context
from .shared import Member, MemberStatus
from .verify_token import verify_token


async def get_caller_member(
    workspace_uuid: str = Path(...),
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> Member:
    """Active Member row of the caller in the URL-path workspace.

    Raises 403 if the user is not a member, is disabled, or is invited-only.
    External collaborators (status=EXTERNAL) are also rejected here — they
    reach scoped resources through their own resource-scoped endpoints.
    """
    # RLS context #1: workspace_uuid set BEFORE the `members` SELECT, so
    # `rls_members_workspace_isolation` filters correctly when RLS is on.
    await set_workspace_context(db, workspace_uuid=workspace_uuid)

    res = await db.execute(
        select(Member).where(
            Member.workspace_uuid == workspace_uuid,
            Member.user_uuid == current_user.uuid,
            Member.status == MemberStatus.ACTIVE,
            Member.deleted_at.is_(None),
        )
    )
    member = res.scalar_one_or_none()
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not an active member of this workspace",
        )

    # RLS context #2: now that the member is resolved, stamp member_uuid so
    # OneOnOne's participant-only policy can identify the caller.
    await set_workspace_context(
        db,
        workspace_uuid=workspace_uuid,
        member_uuid=member.uuid,
    )
    return member
