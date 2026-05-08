from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Payload for creating a new user."""

    name: str
    email: EmailStr
    profile_image_url: str | None = None
    supabase_uuid: UUID | None = None
    auth_id: str | None = None
    access_token: str | None = None


class UserUpdate(BaseModel):
    """Payload for partially updating an existing user."""

    name: str | None = None
    email: EmailStr | None = None
    profile_image_url: str | None = None
    auth_id: str | None = None


class UserRead(BaseModel):
    """Read model exposed by user APIs."""

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
    """Payload for requesting a token refresh."""

    refresh_token: str
