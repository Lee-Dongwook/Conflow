from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base

# Naming note: `Sprint` is mapped to `pm_sprints` because the legacy
# `sprints` table (server/src/app/sprint/model.py) still exists. Once the
# legacy table is migrated out, this can be renamed back to `sprints`.


class ProjectVisibility(enum.Enum):
    PRIVATE = "private"
    INTERNAL = "internal"
    PUBLIC_IN_WORKSPACE = "public_in_workspace"


class ProjectStatus(enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base, AutoUUIDMixin):
    """A grouping of issues with an owner, target date, and visibility scope.

    Linear's Project concept; supersedes the Epic pattern from legacy tools.
    """

    __tablename__ = "projects"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)

    lead_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
    )

    visibility: Mapped[ProjectVisibility] = mapped_column(
        Enum(
            ProjectVisibility,
            name="project_visibility",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ProjectVisibility.PRIVATE,
        nullable=False,
    )

    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(
            ProjectStatus,
            name="project_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ProjectStatus.PLANNED,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_uuid",
            "slug",
            name="uq_projects_workspace_slug",
        ),
        Index("idx_projects_workspace_status", "workspace_uuid", "status"),
        Index("idx_projects_lead", "lead_member_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class SprintPhase(enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class Sprint(Base, AutoUUIDMixin):
    """Time-boxed work unit (Linear's Cycle).

    `project_uuid` is nullable so a Sprint can be workspace-wide rather than
    tied to a single Project.
    """

    __tablename__ = "pm_sprints"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )

    project_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.uuid"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    phase: Mapped[SprintPhase] = mapped_column(
        Enum(
            SprintPhase,
            name="sprint_phase",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=SprintPhase.PLANNED,
        nullable=False,
    )

    # Computed at sprint end; cumulative story points or issue count
    # depending on the workspace's velocity definition.
    velocity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_pm_sprints_workspace_phase", "workspace_uuid", "phase"),
        Index("idx_pm_sprints_project", "project_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class IssueStatus(enum.Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class IssuePriority(enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Issue(Base, AutoUUIDMixin):
    """A single unit of work — the PM domain's core aggregate.

    State machine (docs/02-product/domain-pm.md):
      backlog → todo → in_progress → blocked ↔ in_progress → done | cancelled
    Transitions emit `pm.issue.*` events and are recorded in AuditLog.
    """

    __tablename__ = "issues"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )

    project_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.uuid"),
        nullable=True,
    )

    sprint_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("pm_sprints.uuid"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[IssueStatus] = mapped_column(
        Enum(
            IssueStatus,
            name="issue_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=IssueStatus.BACKLOG,
        nullable=False,
    )

    priority: Mapped[IssuePriority] = mapped_column(
        Enum(
            IssuePriority,
            name="issue_priority",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=IssuePriority.MEDIUM,
        nullable=False,
    )

    reporter_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )

    assignee_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Set when status transitions to BLOCKED; cleared on unblock.
    # `blocked_reason` is exposed by the A2UI tool `pm.identify_blockers`.
    blocked_since: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_issues_workspace_status", "workspace_uuid", "status"),
        Index("idx_issues_workspace_assignee", "workspace_uuid", "assignee_member_uuid"),
        Index("idx_issues_workspace_sprint", "workspace_uuid", "sprint_uuid"),
        Index("idx_issues_workspace_project", "workspace_uuid", "project_uuid"),
        Index("idx_issues_reporter", "reporter_member_uuid"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_blocked(self) -> bool:
        return self.status == IssueStatus.BLOCKED
