from datetime import datetime

from pydantic import BaseModel

from ..user.model import UserRole


class TeamMembershipCreate(BaseModel):
    user_uuid: str
    team_uuid: str
    role: UserRole = UserRole.MEMBER

class TeamMembershipRead(BaseModel):
    uuid: str
    user_uuid: str
    team_uuid: str
    role: UserRole
    joined_at: datetime

class TeamMembershipUpdate(BaseModel):
    role: UserRole | None = None
