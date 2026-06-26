"""Headless PM service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments and returns Pydantic models — no React, no FastAPI
Depends. This is the contract the A2UI Tool Registry depends on
(docs/04-architecture/a2ui-strategy.md).

Authorization is delegated to `core.permissions` — no role logic is inlined
in this file (Watch List #2). Project Maintainer (resource-scoped) lands
with the Documents / external-collaborator step.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.events import (
    PM_ISSUE_BLOCKED,
    PM_ISSUE_CANCELLED,
    PM_ISSUE_CREATED,
    PM_ISSUE_RESOLVED,
    PM_ISSUE_UNBLOCKED,
    emit_event,
)
from ..core.permissions import (
    PermissionDenied,
    is_workspace_admin,
    require_workspace_admin,
    require_workspace_member,
    require_workspace_writer,
)
from ..core.shared import AuditDomain, AuditLog, RoleName
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

# Transition → outbox event map. Keyed by (prev, new) so we can distinguish
# `unblocked` (only from BLOCKED) from a generic enter-in_progress.
_TRANSITION_EVENTS: dict[tuple[IssueStatus, IssueStatus], str] = {
    (IssueStatus.TODO, IssueStatus.BLOCKED): PM_ISSUE_BLOCKED,
    (IssueStatus.IN_PROGRESS, IssueStatus.BLOCKED): PM_ISSUE_BLOCKED,
    (IssueStatus.BLOCKED, IssueStatus.IN_PROGRESS): PM_ISSUE_UNBLOCKED,
    (IssueStatus.IN_PROGRESS, IssueStatus.DONE): PM_ISSUE_RESOLVED,
    (IssueStatus.BACKLOG, IssueStatus.CANCELLED): PM_ISSUE_CANCELLED,
    (IssueStatus.TODO, IssueStatus.CANCELLED): PM_ISSUE_CANCELLED,
    (IssueStatus.IN_PROGRESS, IssueStatus.CANCELLED): PM_ISSUE_CANCELLED,
    (IssueStatus.BLOCKED, IssueStatus.CANCELLED): PM_ISSUE_CANCELLED,
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


def _can_modify_issue(
    issue: Issue,
    *,
    caller_member_uuid: str,
    roles: set[RoleName],
) -> bool:
    """Issue write authority (per docs/02-product/domain-pm.md):
    reporter, assignee, or workspace Admin. Project Maintainer is TBD.
    """
    return (
        issue.reporter_member_uuid == caller_member_uuid
        or issue.assignee_member_uuid == caller_member_uuid
        or is_workspace_admin(roles)
    )


async def create_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: IssueCreateInput,
    db: AsyncSession,
) -> IssueReadOutput:
    await require_workspace_writer(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
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
    await db.flush()  # populate issue.uuid before AuditLog / outbox
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
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=PM_ISSUE_CREATED,
        payload={
            "issue_uuid": issue.uuid,
            "reporter_member_uuid": issue.reporter_member_uuid,
            "assignee_member_uuid": issue.assignee_member_uuid,
            "project_uuid": issue.project_uuid,
            "sprint_uuid": issue.sprint_uuid,
            "priority": issue.priority.value,
        },
    )
    await db.commit()
    await db.refresh(issue)
    return IssueReadOutput.model_validate(issue)


async def get_issue(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    issue_uuid: str,
    db: AsyncSession,
) -> IssueReadOutput:
    # Workspace membership grants issue read; Project visibility (private)
    # scoping is enforced when the Project entity gets its permission layer.
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    return IssueReadOutput.model_validate(issue)


async def list_issues(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: IssueListFilter,
    db: AsyncSession,
) -> IssueListOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
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
    roles = await require_workspace_writer(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    if not _can_modify_issue(issue, caller_member_uuid=caller_member_uuid, roles=roles):
        raise PermissionDenied("Only reporter, assignee, or workspace Admin may update")
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
    roles = await require_workspace_writer(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    issue = await _get_issue_or_404(
        db, workspace_uuid=workspace_uuid, issue_uuid=issue_uuid
    )
    if not _can_modify_issue(issue, caller_member_uuid=caller_member_uuid, roles=roles):
        raise PermissionDenied(
            "Only reporter, assignee, or workspace Admin may transition"
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

    # Outbox event for the subset of transitions that downstream domains
    # actually react to. backlog↔todo / in_progress↔todo are routine and
    # tracked via AuditLog only.
    event_name = _TRANSITION_EVENTS.get((prev_status, new_status))
    if event_name is not None:
        event_payload: dict = {
            "issue_uuid": issue.uuid,
            "assignee_member_uuid": issue.assignee_member_uuid,
            "from": prev_status.value,
            "to": new_status.value,
        }
        if event_name == PM_ISSUE_BLOCKED:
            event_payload["blocked_reason"] = payload.blocked_reason
        emit_event(
            db,
            workspace_uuid=workspace_uuid,
            event_name=event_name,
            payload=event_payload,
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
    # Hard rule: workspace Admin only. Project Maintainer override lands
    # with the Project visibility / resource-scoped permission step.
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
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
