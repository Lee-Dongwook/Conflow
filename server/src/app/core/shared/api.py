"""HTTP routes for the Shared Core (Workspace + Member lifecycle).

- `POST /workspaces`                  — create (signup-tier, no caller Member yet)
- `POST /workspaces/{ws}/members/invite`              — Admin invites by email
- `POST /workspaces/{ws}/members/{uuid}/accept`       — invitee accepts after signup

The accept endpoint deliberately does NOT use `get_caller_member`: at
acceptance time the user is not yet an active Member of the workspace.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...user.schemas import UserRead
from ..database import get_async_db
from ..deps import get_caller_member
from ..verify_token import verify_token
from .member import Member
from .service import (
    MemberInviteInput,
    MemberInviteOutput,
    MemberReadOutput,
    WorkspaceCreateInput,
    WorkspaceReadOutput,
    accept_invitation,
    create_workspace,
    invite_member,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post(
    "",
    response_model=WorkspaceReadOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_endpoint(
    payload: WorkspaceCreateInput,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> WorkspaceReadOutput:
    return await create_workspace(
        creator_user_uuid=current_user.uuid,
        payload=payload,
        db=db,
    )


@router.post(
    "/{workspace_uuid}/members/invite",
    response_model=MemberInviteOutput,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member_endpoint(
    payload: MemberInviteInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> MemberInviteOutput:
    return await invite_member(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.post(
    "/{workspace_uuid}/members/{invited_member_uuid}/accept",
    response_model=MemberReadOutput,
)
async def accept_invitation_endpoint(
    workspace_uuid: str = Path(...),
    invited_member_uuid: str = Path(...),
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> MemberReadOutput:
    return await accept_invitation(
        workspace_uuid=workspace_uuid,
        invited_member_uuid=invited_member_uuid,
        caller_user_uuid=current_user.uuid,
        db=db,
    )
