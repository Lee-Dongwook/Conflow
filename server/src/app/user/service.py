from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .model import User


def not_found_exc():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

async def get_user_with_memberships(db: AsyncSession, user_uuid: str):
    res = await db.execute(select(User).where(User.uuid==user_uuid))
    user = res.scalar_one_or_none()
    if not user:
        raise not_found_exc()
    # memberships loaded by relationship
    return user
