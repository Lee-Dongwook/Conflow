from datetime import datetime

from pydantic import BaseModel

from .model import TeamMemberRole

# -- Team --


class TeamCreate(BaseModel):
    name: str
    description: str | None = None


class TeamRead(BaseModel):
    uuid: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


# -- TeamMembership --


class TeamMembershipCreate(BaseModel):
    user_uuid: str
    team_uuid: str = ""
    role: TeamMemberRole = TeamMemberRole.MEMBER


class TeamMembershipRead(BaseModel):
    uuid: str
    user_uuid: str
    team_uuid: str
    role: TeamMemberRole
    joined_at: datetime


class TeamMembershipUpdate(BaseModel):
    role: TeamMemberRole | None = None
