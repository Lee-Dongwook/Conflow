"""HTTP routes for user CRUD operations."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from .schemas import UserCreate, UserRead, UserUpdate
from .service import create_user, delete_user, get_user_or_404, list_users, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_route(
    payload: UserCreate,
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    """Create a new user."""

    user = await create_user(db, payload)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def list_users_route(
    include_deleted: bool = Query(default=False),
    db: AsyncSession = Depends(get_async_db),
) -> list[UserRead]:
    """List users with optional deleted rows."""

    users = await list_users(db, include_deleted=include_deleted)
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_uuid}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_route(
    user_uuid: str,
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    """Read a single active user by UUID."""

    user = await get_user_or_404(db, user_uuid)
    return UserRead.model_validate(user)


@router.patch("/{user_uuid}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user_route(
    user_uuid: str,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    """Partially update an active user."""

    user = await update_user(db, user_uuid, payload)
    return UserRead.model_validate(user)


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    user_uuid: str,
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """Soft-delete a user by UUID."""

    await delete_user(db, user_uuid)
