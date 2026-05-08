from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    profile_image_url: str | None = None
    supabase_uuid: UUID | None = None
    auth_id: str | None = None
    access_token: str | None = None

class UserRead(BaseModel):
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    uuid: str
    name: str
    email: EmailStr
    profile_image_url: str | None = None
    auth_id: str | None = None

    model_config = ConfigDict(from_attributes=True)

class TokenRefresh(BaseModel):
    refresh_token: str
