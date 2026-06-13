from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import WeekMilestone
from .schemas import WeekMilestoneCreate, WeekMilestoneUpdate


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WeekMilestone not found")


async def list_by_sprint(
    db: AsyncSession,
    sprint_uuid: str,
    *,
    include_completed: bool = True,
) -> list[WeekMilestone]:
    stmt = (
        select(WeekMilestone)
        .where(
            WeekMilestone.sprint_uuid == sprint_uuid,
            WeekMilestone.deleted_at.is_(None),
        )
        .order_by(WeekMilestone.due_on.asc().nulls_last(), WeekMilestone.created_at.asc())
    )
    if not include_completed:
        stmt = stmt.where(WeekMilestone.completed_at.is_(None))
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_or_404(db: AsyncSession, uuid: str) -> WeekMilestone:
    res = await db.execute(
        select(WeekMilestone).where(
            WeekMilestone.uuid == uuid,
            WeekMilestone.deleted_at.is_(None),
        )
    )
    record = res.scalar_one_or_none()
    if not record:
        raise _not_found()
    return record


async def create(db: AsyncSession, payload: WeekMilestoneCreate) -> WeekMilestone:
    record = WeekMilestone(
        sprint_uuid=payload.sprint_uuid,
        owner_user_uuid=payload.owner_user_uuid,
        title=payload.title,
        due_on=payload.due_on,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def update(
    db: AsyncSession,
    uuid: str,
    payload: WeekMilestoneUpdate,
) -> WeekMilestone:
    record = await get_or_404(db, uuid)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)
    await db.commit()
    await db.refresh(record)
    return record


async def set_completed(
    db: AsyncSession,
    uuid: str,
    *,
    completed: bool,
) -> WeekMilestone:
    record = await get_or_404(db, uuid)
    record.completed_at = datetime.now(UTC) if completed else None
    await db.commit()
    await db.refresh(record)
    return record


async def soft_delete(db: AsyncSession, uuid: str) -> None:
    record = await get_or_404(db, uuid)
    record.deleted_at = datetime.now(UTC)
    await db.commit()
