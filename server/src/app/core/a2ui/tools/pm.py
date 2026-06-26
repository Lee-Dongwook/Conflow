"""PM domain Tools — register at import."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

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
