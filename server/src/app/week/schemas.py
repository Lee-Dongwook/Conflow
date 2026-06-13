from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WeekMilestoneCreate(BaseModel):
    sprint_uuid: str
    owner_user_uuid: str
    title: str = Field(min_length=1, max_length=512)
    due_on: datetime | None = None


class WeekMilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    owner_user_uuid: str | None = None
    due_on: datetime | None = None


class WeekMilestoneRead(BaseModel):
    uuid: str
    sprint_uuid: str
    owner_user_uuid: str
    title: str
    due_on: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
