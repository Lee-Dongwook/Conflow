from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DashboardTaskRead(BaseModel):
    """A single task (board card) shown on the dashboard."""

    uuid: str
    title: str
    column_key: str  # todo / doing / done
    assignee_user_uuid: str | None = None
    assignee_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DashboardSprintRead(BaseModel):
    """Sprint summary for the dashboard header."""

    uuid: str
    label: str
    shared_goal: str | None = None
    period_label: str | None = None
    starts_on: datetime
    ends_on: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardMemberRead(BaseModel):
    """Team member info."""

    user_uuid: str
    name: str
    email: str
    profile_image_url: str | None = None
    role: str

    model_config = ConfigDict(from_attributes=True)


class TeamDashboardRead(BaseModel):
    """Aggregated dashboard response for a team."""

    team_uuid: str
    team_name: str
    team_description: str | None = None
    sprint: DashboardSprintRead | None = None
    tasks: list[DashboardTaskRead] = []
    members: list[DashboardMemberRead] = []
    progress_percent: int = 0
    total_tasks: int = 0
    done_tasks: int = 0
    course_label: str | None = None
    blocker_note: str | None = None
    next_deadline_label: str | None = None
