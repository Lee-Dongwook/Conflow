"""Headless PM service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments and returns Pydantic models — no React, no FastAPI
Depends. This is the contract the A2UI Tool Registry depends on
(docs/04-architecture/a2ui-strategy.md).

Permission checks are stubbed (`# PERMISSION-TODO`) and will be wired to
RoleAssignment in the next step.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.shared import AuditDomain, AuditLog
from .model import Issue, IssueStatus
from .schemas import (
    IssueCreateInput,
    IssueListFilter,
    IssueListOutput,
    IssueReadOutput,
    IssueTransitionInput,
    IssueUpdateInput,
)

_VALID_TRANSITIONS: dict[IssueStatus, set[IssueStatus]] = {
    IssueStatus.BACKLOG: {IssueStatus.TODO, IssueStatus.CANCELLED},
    IssueStatus.TODO: {
        IssueStatus.IN_PROGRESS,
        IssueStatus.BLOCKED,
        IssueStatus.CANCELLED,
        IssueStatus.BACKLOG,
    },
    IssueStatus.IN_PROGRESS: {
        IssueStatus.BLOCKED,
        IssueStatus.DONE,
        IssueStatus.CANCELLED,
        IssueStatus.TODO,
    },
    IssueStatus.BLOCKED: {IssueStatus.IN_PROGRESS, IssueStatus.CANCELLED},
    IssueStatus.DONE: set(),
    IssueStatus.CANCELLED: set(),
}

_TRANSITION_ACTIONS: dict[IssueStatus, str] = {
    IssueStatus.BLOCKED: "pm.issue.blocked",
    IssueStatus.IN_PROGRESS: "pm.issue.unblocked",
    IssueStatus.DONE: "pm.issue.resolved",
    IssueStatus.CANCELLED: "pm.issue.cancelled",
}


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _audit(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    actor_member_uuid: str | None,
    action: str,
    issue_uuid: str,
    metadata: dict | None = None,
) -> None:
    """Record a PM mutation in the unified AuditLog. Caller still owns commit."""
    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=actor_member_uuid,
            domain=AuditDomain.PM,
            action=action,
            resource_type="pm.issue",
            resource_uuid=issue_uuid,
            audit_metadata=metadata or {},
        )
    )


async def _get_issue_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    issue_uuid: str,
) -> Issue:
    res = await db.execute(
        select(Issue).where(
            Issue.uuid == issue_uuid,
            Issue.workspace_uuid == workspace_uuid,
            Issue.deleted_at.is_(None),
        )
    )
    issue = res.scalar_one_or_none()
    if not issue:
        raise _not_found()
    return issue


async def create_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: IssueCreateInput,
    db: AsyncSession,
) -> IssueReadOutput:
    # PERMISSION-TODO: caller must have role >= MEMBER on this workspace.
    issue = Issue(
        workspace_uuid=workspace_uuid,
        reporter_member_uuid=caller_member_uuid,
        title=payload.title,
        description=payload.description,
        project_uuid=payload.project_uuid,
        sprint_uuid=payload.sprint_uuid,
        priority=payload.priority,
        assignee_member_uuid=payload.assignee_member_uuid,
        due_date=payload.due_date,
    )
    db.add(issue)
    await db.flush()  # populate issue.uuid before AuditLog
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="pm.issue.created",
        issue_uuid=issue.uuid,
        metadata={
            "title": issue.title,
            "priority": issue.priority.value,
            "assignee_member_uuid": issue.assignee_member_uuid,
        },
    )
    await db.commit()
    await db.refresh(issue)
    return IssueReadOutput.model_validate(issue)


async def get_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,  # noqa: ARG001  # PERMISSION-TODO
    issue_uuid: str,
    db: AsyncSession,
) -> IssueReadOutput:
    # PERMISSION-TODO: caller must be able to read this issue
    # (workspace Member, or Project member if project is private).
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    return IssueReadOutput.model_validate(issue)


async def list_issues(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,  # noqa: ARG001  # PERMISSION-TODO
    filters: IssueListFilter,
    db: AsyncSession,
) -> IssueListOutput:
    # PERMISSION-TODO: scope to projects the caller can see.
    base = select(Issue).where(
        Issue.workspace_uuid == workspace_uuid,
        Issue.deleted_at.is_(None),
    )
    if filters.status is not None:
        base = base.where(Issue.status == filters.status)
    if filters.assignee_member_uuid is not None:
        base = base.where(Issue.assignee_member_uuid == filters.assignee_member_uuid)
    if filters.sprint_uuid is not None:
        base = base.where(Issue.sprint_uuid == filters.sprint_uuid)
    if filters.project_uuid is not None:
        base = base.where(Issue.project_uuid == filters.project_uuid)

    total_res = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total = int(total_res.scalar_one())

    page_res = await db.execute(
        base.order_by(Issue.created_at.desc()).limit(filters.limit).offset(filters.offset)
    )
    issues = [IssueReadOutput.model_validate(i) for i in page_res.scalars().all()]
    return IssueListOutput(issues=issues, total=total)


async def update_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    issue_uuid: str,
    payload: IssueUpdateInput,
    db: AsyncSession,
) -> IssueReadOutput:
    # PERMISSION-TODO: reporter, assignee, project maintainer, or workspace admin.
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return IssueReadOutput.model_validate(issue)
    for attr, value in changes.items():
        setattr(issue, attr, value)
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="pm.issue.updated",
        issue_uuid=issue.uuid,
        metadata={"fields": sorted(changes.keys())},
    )
    await db.commit()
    await db.refresh(issue)
    return IssueReadOutput.model_validate(issue)


async def transition_issue_status(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    issue_uuid: str,
    payload: IssueTransitionInput,
    db: AsyncSession,
) -> IssueReadOutput:
    # PERMISSION-TODO: reporter, assignee, project maintainer, or workspace admin.
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    new_status = payload.new_status
    if new_status == issue.status:
        return IssueReadOutput.model_validate(issue)

    allowed = _VALID_TRANSITIONS[issue.status]
    if new_status not in allowed:
        raise _bad_request(
            f"Illegal transition {issue.status.value} -> {new_status.value}"
        )

    if new_status == IssueStatus.BLOCKED and not payload.blocked_reason:
        raise _bad_request("blocked_reason is required when transitioning to BLOCKED")

    prev_status = issue.status
    issue.status = new_status

    now = datetime.now(timezone.utc)  # noqa: UP017
    if new_status == IssueStatus.BLOCKED:
        issue.blocked_since = now
        issue.blocked_reason = payload.blocked_reason
    elif prev_status == IssueStatus.BLOCKED:
        issue.blocked_since = None
        issue.blocked_reason = None

    action = _TRANSITION_ACTIONS.get(new_status, "pm.issue.transitioned")
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action=action,
        issue_uuid=issue.uuid,
        metadata={
            "from": prev_status.value,
            "to": new_status.value,
            "blocked_reason": payload.blocked_reason,
        },
    )
    await db.commit()
    await db.refresh(issue)
    return IssueReadOutput.model_validate(issue)


async def delete_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    issue_uuid: str,
    db: AsyncSession,
) -> None:
    # PERMISSION-TODO: project maintainer or workspace admin only.
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    issue.deleted_at = datetime.now(timezone.utc)  # noqa: UP017
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="pm.issue.deleted",
        issue_uuid=issue.uuid,
    )
    await db.commit()
