from datetime import datetime

from pydantic import BaseModel, ConfigDict

# -- Sprint --


class SprintCreate(BaseModel):
    team_uuid: str
    label: str
    starts_on: datetime
    ends_on: datetime
    shared_goal: str | None = None
    period_label: str | None = None


class SprintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    team_uuid: str
    label: str
    starts_on: datetime
    ends_on: datetime
    shared_goal: str | None
    period_label: str | None
    created_at: datetime
    updated_at: datetime


class SprintUpdate(BaseModel):
    label: str | None = None
    starts_on: datetime | None = None
    ends_on: datetime | None = None
    shared_goal: str | None = None
    period_label: str | None = None
