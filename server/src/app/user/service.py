from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..common.models import resource_registry
from .model import User, UserRole
from .schemas import UserCreate, UserUpdate


def not_found_exc():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


async def get_user_by_uuid(user_uuid: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    return result.scalars().first()


async def get_user_by_supabase_uuid(supabase_uuid: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.supabase_uuid == supabase_uuid))
    return result.scalars().first()


async def select_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_or_404(db: AsyncSession, user_uuid: str) -> User:
    user = await get_user_by_uuid(user_uuid, db)
    if not user or user.deleted_at is not None:
        raise not_found_exc()
    return user


async def get_user_with_memberships(db: AsyncSession, user_uuid: str) -> User:
    result = await db.execute(
        select(User)
        .where(User.uuid == user_uuid)
        .options(selectinload(User.team_memberships))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise not_found_exc()
    return user


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(
        uuid=resource_registry.generate(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        name=payload.name,
        email=payload.email,
        profile_image_url=payload.profile_image_url or "",
        supabase_uuid=str(payload.supabase_uuid) if payload.supabase_uuid else None,
        auth_id=payload.auth_id,
        role=UserRole.USER,
    )
    db.add(user)
    await db.flush()
    return user


async def list_users(db: AsyncSession, *, include_deleted: bool = False) -> list[User]:
    query = select(User)
    if not include_deleted:
        query = query.where(User.deleted_at.is_(None))
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user_uuid: str, payload: UserUpdate) -> User:
    user = await get_user_or_404(db, user_uuid)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    user.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return user


async def delete_user(db: AsyncSession, user_uuid: str) -> None:
    user = await get_user_or_404(db, user_uuid)
    user.deleted_at = datetime.now(timezone.utc)
    await db.flush()
