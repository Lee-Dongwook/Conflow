from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base

# ---------------------------------------------------------------------------
# RetentionPolicy
# ---------------------------------------------------------------------------


class RetentionPolicy(Base, AutoUUIDMixin):
    """Per-workspace retention rules used by DocumentInstance + RetentionJob.

    `immutable=True` rows represent statutory minimums (e.g. 근로계약서 영구
    or 4대 보험 신고 5년) — must NOT be edited or deleted by tenants.
    """

    __tablename__ = "retention_policies"

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
    # Free text — Tier-aware default + per-category overrides land later.
    # Sentinel value "infinite" or large NULL handled by the retention job.
    retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    immutable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
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
        Index("idx_retention_policies_workspace", "workspace_uuid"),
    )


# ---------------------------------------------------------------------------
# DocumentTemplate
# ---------------------------------------------------------------------------


class DocumentCategory(enum.Enum):
    LABOR = "labor"
    TAX = "tax"
    INTERNAL_ISSUANCE = "internal_issuance"
    EXTERNAL_SUBMISSION = "external_submission"
    REPORT = "report"


class TemplateState(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class DocumentTemplate(Base, AutoUUIDMixin):
    """A reusable document specification. Instances are rendered from these
    against a `variables_snapshot` at issuance time.
    """

    __tablename__ = "document_templates"

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
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[DocumentCategory] = mapped_column(
        Enum(
            DocumentCategory,
            name="document_category",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    subtype: Mapped[str] = mapped_column(String(64), nullable=False)
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    variables_schema: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    # Workflow template (FK lands when ReviewWorkflowTemplate is introduced).
    default_review_workflow_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    default_retention_policy_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("retention_policies.uuid"),
        nullable=False,
    )
    requires_signature: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    state: Mapped[TemplateState] = mapped_column(
        Enum(
            TemplateState,
            name="template_state",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=TemplateState.DRAFT,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_by_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
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
        Index(
            "idx_document_templates_workspace_category_subtype",
            "workspace_uuid",
            "category",
            "subtype",
        ),
        Index(
            "idx_document_templates_workspace_state",
            "workspace_uuid",
            "state",
        ),
    )


# ---------------------------------------------------------------------------
# DocumentInstance
# ---------------------------------------------------------------------------


class DocumentInstanceState(enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SIGNED = "signed"  # KISA signing lands Phase 4
    ISSUED = "issued"
    ARCHIVED = "archived"
    ARCHIVED_LEGAL_ONLY = "archived_legal_only"  # past retention, kept by law
    VOID = "void"


class DocumentInstance(Base, AutoUUIDMixin):
    """A rendered, soon-to-be-issued (or already issued) document.

    `variables_snapshot` freezes the data at issuance time so later HR/PM
    edits never mutate an issued PDF.
    """

    __tablename__ = "document_instances"

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
    template_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("document_templates.uuid"),
        nullable=False,
    )
    template_version: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
    )
    requester_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )
    variables_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    rendered_pdf_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[DocumentInstanceState] = mapped_column(
        Enum(
            DocumentInstanceState,
            name="document_instance_state",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=DocumentInstanceState.DRAFT,
        nullable=False,
    )
    # Forward references to ReviewWorkflow / SignatureRequest (Phase 4) —
    # FK constraint added once those entities ship.
    review_workflow_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    signature_request_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    retention_policy_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("retention_policies.uuid"),
        nullable=False,
    )
    retention_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    __table_args__ = (
        Index(
            "idx_document_instances_workspace_state",
            "workspace_uuid",
            "state",
        ),
        Index(
            "idx_document_instances_workspace_subject_state",
            "workspace_uuid",
            "subject_member_uuid",
            "state",
        ),
        Index(
            "idx_document_instances_workspace_template_created",
            "workspace_uuid",
            "template_uuid",
            "created_at",
        ),
        # Retention sweep hot path: partial index keeps it tiny.
        Index(
            "idx_document_instances_retention_due",
            "retention_expires_at",
            postgresql_where=text("state IN ('issued', 'archived')"),
        ),
    )


# ---------------------------------------------------------------------------
# ReviewWorkflow
# ---------------------------------------------------------------------------


class ReviewWorkflowState(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewWorkflow(Base, AutoUUIDMixin):
    """An ordered review session over a DocumentInstance.

    `review_steps` / `review_comments` tables ship in the next step; this
    aggregate just tracks overall progress + final verdict.
    """

    __tablename__ = "review_workflows"

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
    instance_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("document_instances.uuid"),
        nullable=False,
    )
    steps_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    current_step_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    state: Mapped[ReviewWorkflowState] = mapped_column(
        Enum(
            ReviewWorkflowState,
            name="review_workflow_state",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ReviewWorkflowState.PENDING,
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

    __table_args__ = (
        Index(
            "idx_review_workflows_workspace_instance",
            "workspace_uuid",
            "instance_uuid",
        ),
    )
