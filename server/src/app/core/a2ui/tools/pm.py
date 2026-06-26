"""PM domain Tools — register at import."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....pm.model import Issue, IssueStatus, Sprint, SprintPhase
from ....pm.schemas import (
    IssueCreateInput,
    IssueListFilter,
    IssueListOutput,
    IssueReadOutput,
)
from ....pm.service import create_issue, list_issues
from ...shared import WorkspaceTier
from ..registry import PermissionLevel, ToolSpec, register_tool


async def _pm_search_issues(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: IssueListFilter,
    db: AsyncSession,
) -> IssueListOutput:
    return await list_issues(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        filters=payload,
        db=db,
    )


register_tool(
    ToolSpec(
        id="pm.search_issues",
        domain="pm",
        description=(
            "List issues in the workspace with optional filters "
            "(status / assignee / sprint / project). Paginated."
        ),
        handler=_pm_search_issues,
        input_schema=IssueListFilter,
        output_schema=IssueListOutput,
        min_tier=WorkspaceTier.FREE,
        permission_required=PermissionLevel.MEMBER,
        phase=1,
    )
)


async def _pm_create_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: IssueCreateInput,
    db: AsyncSession,
) -> IssueReadOutput:
    return await create_issue(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        payload=payload,
        db=db,
    )


register_tool(
    ToolSpec(
        id="pm.create_issue",
        domain="pm",
        description=(
            "Create a new issue with title, description, priority, and "
            "optional assignee / sprint / project / due_date."
        ),
        handler=_pm_create_issue,
        input_schema=IssueCreateInput,
        output_schema=IssueReadOutput,
        min_tier=WorkspaceTier.TEAM,
        permission_required=PermissionLevel.WRITER,
        phase=1,
    )
)


# ---------------------------------------------------------------------------
# pm.identify_blockers — issues currently BLOCKED (optionally older than N hours)
# ---------------------------------------------------------------------------


class PmIdentifyBlockersInput(BaseModel):
    min_blocked_hours: int = Field(
        default=0,
        ge=0,
        description="Only return blockers stuck at least this many hours.",
    )
    limit: int = Field(default=50, ge=1, le=200)


async def _pm_identify_blockers(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: PmIdentifyBlockersInput,
    db: AsyncSession,
) -> IssueListOutput:
    filt = IssueListFilter(status=IssueStatus.BLOCKED, limit=payload.limit)
    out = await list_issues(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        filters=filt,
        db=db,
    )
    if payload.min_blocked_hours > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(  # noqa: UP017
            hours=payload.min_blocked_hours
        )
        out.issues = [
            i for i in out.issues if i.blocked_since is not None and i.blocked_since <= cutoff
        ]
        out.total = len(out.issues)
    return out


register_tool(
    ToolSpec(
        id="pm.identify_blockers",
        domain="pm",
        description=(
            "List issues currently in BLOCKED status with their "
            "blocked_reason and stuck duration. Used by the blocker_triage "
            "worker and as an A2UI sub-tool for cross-domain queries."
        ),
        handler=_pm_identify_blockers,
        input_schema=PmIdentifyBlockersInput,
        output_schema=IssueListOutput,
        min_tier=WorkspaceTier.TEAM,
        permission_required=PermissionLevel.MEMBER,
        phase=1,
    )
)


# ---------------------------------------------------------------------------
# pm.get_sprint_summary — Sprint header + issue counts by status
# ---------------------------------------------------------------------------


class PmGetSprintSummaryInput(BaseModel):
    sprint_uuid: str


class PmSprintSummaryOutput(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    sprint_uuid: str
    name: str
    phase: SprintPhase
    start_date: datetime
    end_date: datetime
    velocity: int | None
    issue_count_by_status: dict[str, int]
    blocker_count: int


async def _pm_get_sprint_summary(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,  # noqa: ARG001  permission enforced by dispatcher
    payload: PmGetSprintSummaryInput,
    db: AsyncSession,
) -> PmSprintSummaryOutput:
    sprint_res = await db.execute(
        select(Sprint).where(
            Sprint.uuid == payload.sprint_uuid,
            Sprint.workspace_uuid == workspace_uuid,
            Sprint.deleted_at.is_(None),
        )
    )
    sprint = sprint_res.scalar_one_or_none()
    if sprint is None:
        from fastapi import HTTPException, status  # noqa: PLC0415
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
        )

    counts_res = await db.execute(
        select(Issue.status, func.count())
        .where(
            Issue.workspace_uuid == workspace_uuid,
            Issue.sprint_uuid == sprint.uuid,
            Issue.deleted_at.is_(None),
        )
        .group_by(Issue.status)
    )
    counts: dict[str, int] = {s.value: c for s, c in counts_res.all()}

    return PmSprintSummaryOutput(
        sprint_uuid=sprint.uuid,
        name=sprint.name,
        phase=sprint.phase,
        start_date=sprint.start_date,
        end_date=sprint.end_date,
        velocity=sprint.velocity,
        issue_count_by_status=counts,
        blocker_count=counts.get(IssueStatus.BLOCKED.value, 0),
    )


register_tool(
    ToolSpec(
        id="pm.get_sprint_summary",
        domain="pm",
        description=(
            "Get a sprint header + issue counts grouped by status + blocker count."
        ),
        handler=_pm_get_sprint_summary,
        input_schema=PmGetSprintSummaryInput,
        output_schema=PmSprintSummaryOutput,
        min_tier=WorkspaceTier.TEAM,
        permission_required=PermissionLevel.MEMBER,
        phase=1,
    )
)
