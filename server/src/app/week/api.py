"""REST API for WeekMilestone — the 'this-week goals' surface."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import WeekMilestoneCreate, WeekMilestoneRead, WeekMilestoneUpdate
from .service import (
    create,
    list_by_sprint,
    set_completed,
    soft_delete,
    update,
)

router = APIRouter(prefix="/week-milestones", tags=["week-milestones"])


@router.get("", response_model=list[WeekMilestoneRead])
async def list_milestones(
    sprint_uuid: str = Query(..., min_length=1),
    include_completed: bool = Query(default=True),
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    records = await list_by_sprint(
        db, sprint_uuid, include_completed=include_completed,
    )
    return [WeekMilestoneRead.model_validate(r) for r in records]


@router.post("", response_model=WeekMilestoneRead, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    payload: WeekMilestoneCreate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    record = await create(db, payload)
    return WeekMilestoneRead.model_validate(record)


@router.patch("/{uuid}", response_model=WeekMilestoneRead)
async def update_milestone(
    uuid: str,
    payload: WeekMilestoneUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    record = await update(db, uuid, payload)
    return WeekMilestoneRead.model_validate(record)


@router.post("/{uuid}/complete", response_model=WeekMilestoneRead)
async def complete_milestone(
    uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    record = await set_completed(db, uuid, completed=True)
    return WeekMilestoneRead.model_validate(record)


@router.post("/{uuid}/uncomplete", response_model=WeekMilestoneRead)
async def uncomplete_milestone(
    uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    record = await set_completed(db, uuid, completed=False)
    return WeekMilestoneRead.model_validate(record)


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    await soft_delete(db, uuid)
