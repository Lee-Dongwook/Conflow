from datetime import datetime

from pydantic import BaseModel


class BoardCardCreate(BaseModel):
    team_uuid: str
    sprint_uuid: str
    title: str
    column_key: str = "todo"
    description: str | None = None
    position: int = 0
    assignee_user_uuid: str | None = None
    reporter_user_uuid: str | None = None


class BoardCardRead(BaseModel):
    uuid: str
    team_uuid: str
    sprint_uuid: str
    title: str
    column_key: str
    description: str | None
    position: int
    assignee_user_uuid: str | None
    reporter_user_uuid: str | None
    created_at: datetime
    updated_at: datetime


class BoardCardUpdate(BaseModel):
    title: str | None = None
    column_key: str | None = None
    description: str | None = None
    position: int | None = None
    assignee_user_uuid: str | None = None
    reporter_user_uuid: str | None = None


class BoardCardMove(BaseModel):
    """Move a card to a different column and/or position."""

    column_key: str
    position: int


class BoardCardPositionItem(BaseModel):
    uuid: str
    column_key: str
    position: int


class BoardCardBulkPositionUpdate(BaseModel):
    """Reorder multiple cards at once (after drag-and-drop)."""

    items: list[BoardCardPositionItem]
