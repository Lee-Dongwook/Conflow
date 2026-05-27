"""REST API for Team and TeamMembership."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import (
    TeamCreate,
    TeamMembershipCreate,
    TeamMembershipRead,
    TeamMembershipUpdate,
    TeamRead,
)
from .service import (
    create_membership,
    create_team,
    delete_membership,
    delete_team,
    get_membership_or_404,
    get_team_or_404,
    list_team_memberships,
    update_membership,
)

router = APIRouter(prefix="/teams", tags=["teams"])


# -- Team endpoints --


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team_endpoint(
    payload: TeamCreate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new team. The creator automatically becomes the OWNER."""
    team = await create_team(db, payload, current_user.uuid)
    return TeamRead.model_validate(team)


@router.get("/{team_uuid}", response_model=TeamRead)
async def get_team(
    team_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    team = await get_team_or_404(db, team_uuid)
    return TeamRead.model_validate(team)


@router.delete("/{team_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_endpoint(
    team_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a team. Only the OWNER can delete."""
    await delete_team(db, team_uuid, current_user.uuid)


# -- Membership endpoints --


@router.post(
    "/{team_uuid}/memberships",
    response_model=TeamMembershipRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_team_membership(
    team_uuid: str,
    payload: TeamMembershipCreate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    """Add a user to a team."""
    payload.team_uuid = team_uuid
    membership = await create_membership(db, payload)
    return TeamMembershipRead.model_validate(membership)


@router.get("/{team_uuid}/memberships", response_model=list[TeamMembershipRead])
async def list_memberships(
    team_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    memberships = await list_team_memberships(db, team_uuid)
    return [TeamMembershipRead.model_validate(m) for m in memberships]


@router.get("/memberships/{membership_uuid}", response_model=TeamMembershipRead)
async def get_membership(
    membership_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    m = await get_membership_or_404(db, membership_uuid)
    return TeamMembershipRead.model_validate(m)


@router.patch("/memberships/{membership_uuid}", response_model=TeamMembershipRead)
async def update_team_membership(
    membership_uuid: str,
    payload: TeamMembershipUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    m = await update_membership(db, membership_uuid, payload)
    return TeamMembershipRead.model_validate(m)


@router.delete("/memberships/{membership_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_membership(
    membership_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    await delete_membership(db, membership_uuid)
