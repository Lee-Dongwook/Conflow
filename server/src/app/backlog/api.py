"""REST API for Backlog CRUD."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import (
    BacklogItemCreate,
    BacklogItemRead,
    BacklogItemUpdate,
    BacklogPriorityUpdate,
)
from .service import (
    bulk_update_priorities,
    create_backlog_item,
    delete_backlog_item,
    get_backlog_item_or_404,
    list_backlog_items_by_sprint,
    update_backlog_item,
)

router = APIRouter(prefix="/backlogs", tags=["backlogs"])


@router.post("", response_model=BacklogItemRead, status_code=status.HTTP_201_CREATED)
async def create_backlog_endpoint(
    payload: BacklogItemCreate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    item = await create_backlog_item(db, payload)
    return BacklogItemRead.model_validate(item)


@router.get("/sprint/{sprint_uuid}", response_model=list[BacklogItemRead])
async def list_backlogs(
    sprint_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    items = await list_backlog_items_by_sprint(db, sprint_uuid)
    return [BacklogItemRead.model_validate(i) for i in items]


@router.patch("/priorities/bulk", response_model=list[BacklogItemRead])
async def bulk_update_priorities_endpoint(
    payload: BacklogPriorityUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    items = await bulk_update_priorities(db, payload)
    return [BacklogItemRead.model_validate(i) for i in items]


@router.get("/{item_uuid}", response_model=BacklogItemRead)
async def get_backlog(
    item_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    item = await get_backlog_item_or_404(db, item_uuid)
    return BacklogItemRead.model_validate(item)


@router.patch("/{item_uuid}", response_model=BacklogItemRead)
async def update_backlog_endpoint(
    item_uuid: str,
    payload: BacklogItemUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    item = await update_backlog_item(db, item_uuid, payload)
    return BacklogItemRead.model_validate(item)


@router.delete("/{item_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backlog_endpoint(
    item_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    await delete_backlog_item(db, item_uuid)
