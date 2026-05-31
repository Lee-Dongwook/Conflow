from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .model import BacklogItem
from .schemas import BacklogItemCreate, BacklogItemUpdate, BacklogPriorityUpdate


def _not_found():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backlog item not found")


async def create_backlog_item(db: AsyncSession, payload: BacklogItemCreate) -> BacklogItem:
    item = BacklogItem(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_backlog_item_or_404(db: AsyncSession, item_uuid: str) -> BacklogItem:
    res = await db.execute(
        select(BacklogItem).where(
            BacklogItem.uuid == item_uuid, BacklogItem.deleted_at.is_(None)
        )
    )
    item = res.scalar_one_or_none()
    if not item:
        raise _not_found()
    return item


async def list_backlog_items_by_sprint(
    db: AsyncSession, sprint_uuid: str
) -> list[BacklogItem]:
    res = await db.execute(
        select(BacklogItem).where(
            BacklogItem.sprint_uuid == sprint_uuid, BacklogItem.deleted_at.is_(None)
        )
    )
    return list(res.scalars().all())


async def update_backlog_item(
    db: AsyncSession, item_uuid: str, payload: BacklogItemUpdate
) -> BacklogItem:
    item = await get_backlog_item_or_404(db, item_uuid)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, attr, value)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_backlog_item(db: AsyncSession, item_uuid: str) -> None:
    item = await get_backlog_item_or_404(db, item_uuid)
    item.deleted_at = datetime.now(UTC)
    await db.commit()


async def bulk_update_priorities(
    db: AsyncSession, payload: BacklogPriorityUpdate
) -> list[BacklogItem]:
    items = []
    for entry in payload.items:
        item = await get_backlog_item_or_404(db, entry.uuid)
        item.priority = entry.priority
        items.append(item)
    await db.commit()
    for item in items:
        await db.refresh(item)
    return items
