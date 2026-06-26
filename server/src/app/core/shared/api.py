"""HTTP routes for the Shared Core (Workspace lifecycle).

A Workspace is created by an authenticated User (Supabase signup) and the
service seeds the five canonical Roles + an OWNER RoleAssignment for the
creator in the same transaction. There is no `caller_member` here because
the caller has no Member row yet.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...user.schemas import UserRead
from ..database import get_async_db
from ..verify_token import verify_token
from .service import (
    WorkspaceCreateInput,
    WorkspaceReadOutput,
    create_workspace,
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
