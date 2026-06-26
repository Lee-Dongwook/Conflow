from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...common.models import AutoUUIDMixin
from ..database import Base


class AuditDomain(enum.Enum):
    PM = "pm"
    COMMS = "comms"
    HR = "hr"
    DOCUMENTS = "documents"
    SYSTEM = "system"  # workspace lifecycle, scheduled jobs, migrations


class AuditLog(Base, AutoUUIDMixin):
    """Unified audit trail across all four domains.

    Immutable by design: no `updated_at` / `deleted_at`. Retention is enforced
    by a separate Tier-aware cleanup job (Phase 3+), not by row mutation.
    SOC2 Type II (Phase 3) and K-ISMS (Phase 4) certifications depend on this
    table being the single source of truth — see Watch List #7 in
    docs/02-product/domain-overview.md ("도메인별 audit_* 테이블 신설" 금지).
    """

    __tablename__ = "audit_logs"

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

    # Nullable: system actions (scheduled jobs, migrations) have no human actor.
    actor_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
    )

    domain: Mapped[AuditDomain] = mapped_column(
        Enum(
            AuditDomain,
            name="audit_domain",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(String(64), nullable=False)

    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # `metadata` is reserved on SQLAlchemy's Declarative Base; map the Python
    # attribute to a `metadata` column at the DB level so the schema matches
    # docs/04-architecture/data-model.md.
    audit_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )

    # OpenTelemetry trace id (32-char hex). Nullable until tracing rolls out.
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index(
            "idx_audit_logs_workspace_occurred",
            "workspace_uuid",
            "occurred_at",
        ),
        Index(
            "idx_audit_logs_workspace_domain_action",
            "workspace_uuid",
            "domain",
            "action",
        ),
        Index("idx_audit_logs_actor", "actor_member_uuid"),
    )
