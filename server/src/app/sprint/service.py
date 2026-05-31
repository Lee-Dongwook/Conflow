from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .model import Sprint
from .schemas import SprintCreate, SprintUpdate


def _not_found():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")


async def create_sprint(db: AsyncSession, payload: SprintCreate) -> Sprint:
    sprint = Sprint(**payload.model_dump())
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    return sprint


async def get_sprint_or_404(db: AsyncSession, sprint_uuid: str) -> Sprint:
    res = await db.execute(
        select(Sprint).where(Sprint.uuid == sprint_uuid, Sprint.deleted_at.is_(None))
    )
    sprint = res.scalar_one_or_none()
    if not sprint:
        raise _not_found()
    return sprint


async def list_sprints_by_team(db: AsyncSession, team_uuid: str) -> list[Sprint]:
    res = await db.execute(
        select(Sprint).where(Sprint.team_uuid == team_uuid, Sprint.deleted_at.is_(None))
    )
    return list(res.scalars().all())


async def update_sprint(
    db: AsyncSession, sprint_uuid: str, payload: SprintUpdate
) -> Sprint:
    sprint = await get_sprint_or_404(db, sprint_uuid)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(sprint, attr, value)
    await db.commit()
    await db.refresh(sprint)
    return sprint


async def delete_sprint(db: AsyncSession, sprint_uuid: str) -> None:
    sprint = await get_sprint_or_404(db, sprint_uuid)
    sprint.deleted_at = datetime.now(UTC)
    await db.commit()
