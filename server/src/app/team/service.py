from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .model import Team, TeamMemberRole, TeamMembership


def not_found_exc(detail: str = "TeamMembership not found"):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# -- Team CRUD --


async def create_team(db: AsyncSession, payload, creator_uuid: str) -> Team:
    """Create a team and add the creator as OWNER."""
    team = Team(name=payload.name, description=payload.description)
    db.add(team)
    await db.flush()

    membership = TeamMembership(
        user_uuid=creator_uuid,
        team_uuid=team.uuid,
        role=TeamMemberRole.OWNER,
    )
    db.add(membership)
    await db.commit()

    # re-fetch with sprints eager-loaded (async session cannot lazy-load)
    return await get_team_or_404(db, team.uuid)


async def get_team_or_404(db: AsyncSession, team_uuid: str) -> Team:
    res = await db.execute(
        select(Team)
        .where(Team.uuid == team_uuid, Team.deleted_at.is_(None))
        .options(selectinload(Team.sprints))
    )
    team = res.scalar_one_or_none()
    if not team:
        raise not_found_exc("Team not found")
    return team


async def delete_team(db: AsyncSession, team_uuid: str, user_uuid: str) -> None:
    """Delete a team. Only the OWNER can delete."""
    team = await get_team_or_404(db, team_uuid)
    await _require_owner(db, team_uuid, user_uuid)
    await db.delete(team)
    await db.commit()


async def _require_owner(db: AsyncSession, team_uuid: str, user_uuid: str) -> TeamMembership:
    """Raise 403 if the user is not an OWNER of the team."""
    res = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_uuid == team_uuid,
            TeamMembership.user_uuid == user_uuid,
            TeamMembership.deleted_at.is_(None),
        )
    )
    membership = res.scalar_one_or_none()
    if not membership or membership.role != TeamMemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team owner can perform this action",
        )
    return membership


# -- Membership CRUD --


async def create_membership(db: AsyncSession, payload):
    membership = TeamMembership(**payload.model_dump())
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def get_membership_or_404(db: AsyncSession, uuid: str):
    res = await db.execute(select(TeamMembership).where(TeamMembership.uuid == uuid))
    membership = res.scalar_one_or_none()
    if not membership:
        raise not_found_exc()
    return membership


async def list_team_memberships(db: AsyncSession, team_uuid: str):
    res = await db.execute(select(TeamMembership).where(TeamMembership.team_uuid == team_uuid))
    return res.scalars().all()


async def update_membership(db: AsyncSession, uuid: str, payload):
    membership = await get_membership_or_404(db, uuid)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(membership, attr, value)
    await db.commit()
    await db.refresh(membership)
    return membership


async def delete_membership(db: AsyncSession, uuid: str):
    membership = await get_membership_or_404(db, uuid)
    await db.delete(membership)
    await db.commit()
