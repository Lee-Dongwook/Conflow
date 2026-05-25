from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import User
from .schemas import UserCreate, UserUpdate
from .utils import (
    delete_user as delete_user_by_uuid,
)
from .utils import (
    get_user_by_supabase_uuid,
    get_user_by_uuid,
    insert_user,
    select_user_by_email,
)


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a user after validating email uniqueness."""

    existing_user = await select_user_by_email(str(user_in.email), db)

    if existing_user:
        return existing_user

    new_user = await insert_user(user_in, db)
    return new_user


async def list_users(db: AsyncSession, *, include_deleted: bool = False) -> list[User]:
    """Return users ordered by creation time descending."""
    query = select(User).order_by(User.created_at.desc())
    if not include_deleted:
        query = query.where(User.deleted_at.is_(None))
    users_result = await db.execute(query)
    users = users_result.scalars().all()
    return list (users)

async def get_user(user_uuid: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def get_user_or_404(db: AsyncSession, user_uuid: str) -> User:
    """Return an active user by UUID or raise 404."""

    try:
        normalized_user_uuid = str(UUID(user_uuid))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid user uuid") from exc

    user_query = select(User).where(
        User.uuid == normalized_user_uuid,
        User.deleted_at.is_(None),
    )
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def update_user(db: AsyncSession, user_uuid: str, payload: UserUpdate) -> User:
    """Apply a partial update to an active user."""

    user = await get_user_or_404(db, user_uuid)

    if payload.email is not None:
        email_owner_query = select(User).where(
            User.email == str(payload.email),
            User.uuid != user.uuid,
            User.deleted_at.is_(None),
        )
        email_owner_result = await db.execute(email_owner_query)
        email_owner = email_owner_result.scalar_one_or_none()
        if email_owner is not None:
            raise HTTPException(status_code=409, detail="User with this email already exists")
        user.email = str(payload.email)

    if payload.name is not None:
        user.name = payload.name
    if payload.profile_image_url is not None:
        user.profile_image_url = payload.profile_image_url
    if payload.auth_id is not None:
        user.auth_id = payload.auth_id

    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_uuid: str) -> None:
    """Soft-delete an active user by UUID."""

    await delete_user_by_uuid(user_uuid, db)
