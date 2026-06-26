"""Pydantic Input / Output schemas for PM service functions.

Per docs/04-architecture/a2ui-strategy.md "Schema-first" principle: every
service function exposes Pydantic schemas so it can be lifted into the A2UI
Tool Registry without rework.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .model import IssuePriority, IssueStatus


class IssueCreateInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    project_uuid: str | None = None
    sprint_uuid: str | None = None
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_member_uuid: str | None = None
    due_date: datetime | None = None


class IssueUpdateInput(BaseModel):
    """Partial update; unset fields are not touched.

    Status changes go through `transition_issue_status` (state-machine guard).
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    project_uuid: str | None = None
    sprint_uuid: str | None = None
    priority: IssuePriority | None = None
    assignee_member_uuid: str | None = None
    due_date: datetime | None = None


class IssueTransitionInput(BaseModel):
    """State-machine transition. `blocked_reason` is required when
    transitioning into `BLOCKED` and ignored otherwise.
    """

    new_status: IssueStatus
    blocked_reason: str | None = None


class IssueListFilter(BaseModel):
    status: IssueStatus | None = None
    assignee_member_uuid: str | None = None
    sprint_uuid: str | None = None
    project_uuid: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class IssueReadOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    project_uuid: str | None
    sprint_uuid: str | None
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    reporter_member_uuid: str
    assignee_member_uuid: str | None
    due_date: datetime | None
    blocked_since: datetime | None
    blocked_reason: str | None
    created_at: datetime
    updated_at: datetime


class IssueListOutput(BaseModel):
    issues: list[IssueReadOutput]
    total: int
