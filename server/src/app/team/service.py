from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .model import TeamMembership


def not_found_exc():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TeamMembership not found")

async def create_membership(db: AsyncSession, payload):
    membership = TeamMembership(**payload.model_dump())
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership

async def get_membership_or_404(db: AsyncSession, uuid: str):
    res = await db.execute(select(TeamMembership).where(TeamMembership.uuid==uuid))
    membership = res.scalar_one_or_none()
    if not membership:
        raise not_found_exc()
    return membership

async def list_team_memberships(db: AsyncSession, team_uuid: str):
    res = await db.execute(select(TeamMembership).where(TeamMembership.team_uuid==team_uuid))
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
