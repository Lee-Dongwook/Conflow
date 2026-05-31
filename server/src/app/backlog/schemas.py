from datetime import datetime

from pydantic import BaseModel

from .model import BacklogPriority


class BacklogItemCreate(BaseModel):
    team_uuid: str
    sprint_uuid: str
    title: str
    assignee_user_uuid: str | None = None
    priority: BacklogPriority = BacklogPriority.MEDIUM
    note: str | None = None


class BacklogItemRead(BaseModel):
    uuid: str
    team_uuid: str
    sprint_uuid: str
    title: str
    assignee_user_uuid: str | None
    priority: BacklogPriority
    note: str | None
    created_at: datetime
    updated_at: datetime


class BacklogItemUpdate(BaseModel):
    title: str | None = None
    assignee_user_uuid: str | None = None
    priority: BacklogPriority | None = None
    note: str | None = None
    sprint_uuid: str | None = None


class BacklogPriorityItem(BaseModel):
    uuid: str
    priority: BacklogPriority


class BacklogPriorityUpdate(BaseModel):
    """Bulk reorder: list of backlog item UUIDs with their new priorities."""

    items: list[BacklogPriorityItem]
