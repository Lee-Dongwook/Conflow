from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..common.models import resource_registry
from .model import User, UserRole
from .schemas import UserCreate

async def insert_user(user_in: UserCreate, db: AsyncSession) -> User:
    user = User(
        uuid=resource_registry.generate(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        name=user_in.name,
        email=user_in.email,
        profile_image_url=user_in.profile_image_url or "",
        supabase_uuid=user_in.supabase_uuid,
        auth_id=user_in.auth_id,
        role=UserRole.USER,
    )

    db.add(user)
    await db.flush()
    return user

async def select_user_by_email(email: str, db: AsyncSession) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_supabase_uuid(supabase_uuid: str, db: AsyncSession) -> User | None:
    query = select(User).where(User.supabase_uuid == supabase_uuid)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_uuid(user_uuid: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    return result.scalars().first()

async def delete_user(user_uuid: str, db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.deleted_at = datetime.now(timezone.utc)
    await db.flush()
