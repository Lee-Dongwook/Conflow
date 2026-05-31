"""REST API for Board Card CRUD."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import (
    BoardCardBulkPositionUpdate,
    BoardCardCreate,
    BoardCardMove,
    BoardCardRead,
    BoardCardUpdate,
)
from .service import (
    bulk_update_positions,
    create_board_card,
    delete_board_card,
    get_board_card_or_404,
    list_board_cards_by_sprint,
    move_board_card,
    update_board_card,
)

router = APIRouter(prefix="/board-cards", tags=["board-cards"])


@router.post("", response_model=BoardCardRead, status_code=status.HTTP_201_CREATED)
async def create_card_endpoint(
    payload: BoardCardCreate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    card = await create_board_card(db, payload)
    return BoardCardRead.model_validate(card, from_attributes=True)


@router.get("/sprint/{sprint_uuid}", response_model=list[BoardCardRead])
async def list_cards_by_sprint(
    sprint_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    cards = await list_board_cards_by_sprint(db, sprint_uuid)
    return [BoardCardRead.model_validate(c, from_attributes=True) for c in cards]


@router.get("/{card_uuid}", response_model=BoardCardRead)
async def get_card(
    card_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    card = await get_board_card_or_404(db, card_uuid)
    return BoardCardRead.model_validate(card, from_attributes=True)


@router.patch("/{card_uuid}", response_model=BoardCardRead)
async def update_card_endpoint(
    card_uuid: str,
    payload: BoardCardUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    card = await update_board_card(db, card_uuid, payload)
    return BoardCardRead.model_validate(card, from_attributes=True)


@router.patch("/{card_uuid}/move", response_model=BoardCardRead)
async def move_card_endpoint(
    card_uuid: str,
    payload: BoardCardMove,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    card = await move_board_card(db, card_uuid, payload)
    return BoardCardRead.model_validate(card, from_attributes=True)


@router.delete("/{card_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card_endpoint(
    card_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    await delete_board_card(db, card_uuid)


@router.patch("/positions/bulk", response_model=list[BoardCardRead])
async def bulk_update_positions_endpoint(
    payload: BoardCardBulkPositionUpdate,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    cards = await bulk_update_positions(db, payload)
    return [BoardCardRead.model_validate(c, from_attributes=True) for c in cards]
