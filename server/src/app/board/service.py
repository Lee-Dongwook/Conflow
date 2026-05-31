from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .model import BoardCard
from .schemas import (
    BoardCardBulkPositionUpdate,
    BoardCardCreate,
    BoardCardMove,
    BoardCardUpdate,
)


def _not_found():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board card not found")


async def create_board_card(db: AsyncSession, payload: BoardCardCreate) -> BoardCard:
    card = BoardCard(**payload.model_dump())
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def get_board_card_or_404(db: AsyncSession, card_uuid: str) -> BoardCard:
    res = await db.execute(
        select(BoardCard).where(BoardCard.uuid == card_uuid, BoardCard.deleted_at.is_(None))
    )
    card = res.scalar_one_or_none()
    if not card:
        raise _not_found()
    return card


async def list_board_cards_by_sprint(
    db: AsyncSession, sprint_uuid: str
) -> list[BoardCard]:
    res = await db.execute(
        select(BoardCard)
        .where(BoardCard.sprint_uuid == sprint_uuid, BoardCard.deleted_at.is_(None))
        .order_by(BoardCard.column_key, BoardCard.position)
    )
    return list(res.scalars().all())


async def update_board_card(
    db: AsyncSession, card_uuid: str, payload: BoardCardUpdate
) -> BoardCard:
    card = await get_board_card_or_404(db, card_uuid)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(card, attr, value)
    await db.commit()
    await db.refresh(card)
    return card


async def move_board_card(
    db: AsyncSession, card_uuid: str, payload: BoardCardMove
) -> BoardCard:
    card = await get_board_card_or_404(db, card_uuid)
    card.column_key = payload.column_key
    card.position = payload.position
    await db.commit()
    await db.refresh(card)
    return card


async def delete_board_card(db: AsyncSession, card_uuid: str) -> None:
    card = await get_board_card_or_404(db, card_uuid)
    card.deleted_at = datetime.now(UTC)
    await db.commit()


async def bulk_update_positions(
    db: AsyncSession, payload: BoardCardBulkPositionUpdate
) -> list[BoardCard]:
    cards = []
    for entry in payload.items:
        card = await get_board_card_or_404(db, entry.uuid)
        card.column_key = entry.column_key
        card.position = entry.position
        cards.append(card)
    await db.commit()
    for card in cards:
        await db.refresh(card)
    return cards
