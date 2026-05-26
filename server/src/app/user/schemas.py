from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from .model import UserRole


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
    role: UserRole
    auth_id: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class TeamMembershipRead(BaseModel):
    uuid: str
    user_uuid: str
    team_uuid: str
    role: UserRole
    joined_at: datetime
    class Config:
        orm_mode = True

class UserWithTeamsRead(UserRead):
    team_memberships: list[TeamMembershipRead] | None = None

class TokenRefresh(BaseModel):
    """Payload for requesting a token refresh."""
    refresh_token: str
