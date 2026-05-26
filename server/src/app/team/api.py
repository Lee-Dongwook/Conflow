"""
Minimal REST API for Team using FastAPI.
Now includes TeamMembership CRUD endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from .schemas import TeamMembershipCreate, TeamMembershipRead, TeamMembershipUpdate
from .service import (
    create_membership,
    delete_membership,
    get_membership_or_404,
    list_team_memberships,
    update_membership,
)

router = APIRouter(prefix="/teams", tags=["teams"])

# -- Existing Team CRUD omitted for brevity --

@router.post("/{team_uuid}/memberships", response_model=TeamMembershipRead, status_code=status.HTTP_201_CREATED)
async def add_team_membership(
    team_uuid: str,
    payload: TeamMembershipCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Add a user to a team."""
    data = payload.model_copy()
    data["team_uuid"] = team_uuid
    membership = await create_membership(db, payload)
    return TeamMembershipRead.model_validate(membership)

@router.get("/{team_uuid}/memberships", response_model=list[TeamMembershipRead], status_code=status.HTTP_200_OK)
async def list_memberships(
    team_uuid: str,
    db: AsyncSession = Depends(get_async_db),
):
    """List memberships for a team."""
    memberships = await list_team_memberships(db, team_uuid)
    return [TeamMembershipRead.model_validate(m) for m in memberships]

@router.get("/memberships/{membership_uuid}", response_model=TeamMembershipRead, status_code=status.HTTP_200_OK)
async def get_membership(
    membership_uuid: str,
    db: AsyncSession = Depends(get_async_db),
):
    m = await get_membership_or_404(db, membership_uuid)
    return TeamMembershipRead.model_validate(m)

@router.patch("/memberships/{membership_uuid}", response_model=TeamMembershipRead, status_code=status.HTTP_200_OK)
async def update_team_membership(
    membership_uuid: str,
    payload: TeamMembershipUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    m = await update_membership(db, membership_uuid, payload)
    return TeamMembershipRead.model_validate(m)

@router.delete("/memberships/{membership_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_membership(
    membership_uuid: str,
    db: AsyncSession = Depends(get_async_db),
):
    await delete_membership(db, membership_uuid)
