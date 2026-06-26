"""PM HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.deps import get_caller_member
from ..core.shared import Member
from .schemas import (
    IssueCreateInput,
    IssueListFilter,
    IssueListOutput,
    IssueReadOutput,
    IssueTransitionInput,
    IssueUpdateInput,
)
from .service import (
    create_issue,
    delete_issue,
    get_issue,
    list_issues,
    transition_issue_status,
    update_issue,
)

router = APIRouter(prefix="/workspaces/{workspace_uuid}/issues", tags=["pm"])


@router.post("", response_model=IssueReadOutput, status_code=status.HTTP_201_CREATED)
async def create_issue_endpoint(
    payload: IssueCreateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> IssueReadOutput:
    return await create_issue(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("", response_model=IssueListOutput)
async def list_issues_endpoint(
    workspace_uuid: str = Path(...),
    filters: IssueListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> IssueListOutput:
    return await list_issues(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.get("/{issue_uuid}", response_model=IssueReadOutput)
async def get_issue_endpoint(
    issue_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> IssueReadOutput:
    return await get_issue(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        issue_uuid=issue_uuid,
        db=db,
    )


@router.patch("/{issue_uuid}", response_model=IssueReadOutput)
async def update_issue_endpoint(
    issue_uuid: str,
    payload: IssueUpdateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> IssueReadOutput:
    return await update_issue(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        issue_uuid=issue_uuid,
        payload=payload,
        db=db,
    )


@router.post("/{issue_uuid}/transition", response_model=IssueReadOutput)
async def transition_issue_endpoint(
    issue_uuid: str,
    payload: IssueTransitionInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> IssueReadOutput:
    return await transition_issue_status(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        issue_uuid=issue_uuid,
        payload=payload,
        db=db,
    )


@router.delete("/{issue_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue_endpoint(
    issue_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    await delete_issue(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        issue_uuid=issue_uuid,
        db=db,
    )
