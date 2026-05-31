"""REST API for Sprint CRUD."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import SprintCreate, SprintRead, SprintUpdate
from .service import (
    create_sprint,
    delete_sprint,
    get_sprint_or_404,
    list_sprints_by_team,
    update_sprint,
)

router = APIRouter(prefix="/sprints", tags=["sprints"])


@router.post("", response_model=SprintRead, status_code=status.HTTP_201_CREATED)
async def create_sprint_endpoint(
    payload: SprintCreate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    sprint = await create_sprint(db, payload)
    return SprintRead.model_validate(sprint)


@router.get("/team/{team_uuid}", response_model=list[SprintRead])
async def list_sprints(
    team_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    sprints = await list_sprints_by_team(db, team_uuid)
    return [SprintRead.model_validate(s) for s in sprints]


@router.get("/{sprint_uuid}", response_model=SprintRead)
async def get_sprint(
    sprint_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    sprint = await get_sprint_or_404(db, sprint_uuid)
    return SprintRead.model_validate(sprint)


@router.patch("/{sprint_uuid}", response_model=SprintRead)
async def update_sprint_endpoint(
    sprint_uuid: str,
    payload: SprintUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    sprint = await update_sprint(db, sprint_uuid, payload)
    return SprintRead.model_validate(sprint)


@router.delete("/{sprint_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint_endpoint(
    sprint_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    await delete_sprint(db, sprint_uuid)
