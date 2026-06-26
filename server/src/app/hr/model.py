from __future__ import annotations

import enum
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base


class OrgUnitKind(enum.Enum):
    DEPARTMENT = "department"
    TEAM = "team"
    SQUAD = "squad"


class OrgUnit(Base, AutoUUIDMixin):
    """A node in the org tree (department / team / squad).

    Permission: read = any workspace Member; write = HR Admin + Owner
    (docs/02-product/domain-hr.md).
    """

    __tablename__ = "org_units"

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

    parent_org_unit_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("org_units.uuid"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    manager_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
    )

    kind: Mapped[OrgUnitKind] = mapped_column(
        Enum(
            OrgUnitKind,
            name="org_unit_kind",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    # Phase 4 finance integration; nullable until then.
    cost_center_code: Mapped[str | None] = mapped_column(String(32), nullable=True)

    is_archived: Mapped[bool] = mapped_column(
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
        Index(
            "idx_org_units_workspace_parent",
            "workspace_uuid",
            "parent_org_unit_uuid",
        ),
        Index(
            "idx_org_units_workspace_manager",
            "workspace_uuid",
            "manager_member_uuid",
        ),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class EmploymentType(enum.Enum):
    REGULAR = "regular"
    CONTRACT = "contract"
    OUTSOURCED = "outsourced"
    INTERN = "intern"


class TenureStatus(enum.Enum):
    CANDIDATE = "candidate"
    PRE_HIRE = "pre_hire"
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    PRE_OFFBOARDING = "pre_offboarding"
    OFFBOARDED = "offboarded"
    ARCHIVED_LEGAL = "archived_legal"  # 법정 보존 (통상 3년)


# Per-column privacy classification (docs/02-product/domain-hr.md
# "프라이버시 4계층"). Read by the response masker in the service layer;
# never imported from outside HR.
PRIVACY_PUBLIC = "public"          # workspace-wide visible
PRIVACY_MANAGER = "manager_visible"  # manager + HR + self
PRIVACY_HR_ONLY = "hr_only"        # HR Admin + self
PRIVACY_SELF_ONLY = "self_only"    # self only


class EmployeeProfile(Base, AutoUUIDMixin):
    """The HR extension of `Member` (1:1). The single source of truth for
    employment-type, hire date, org placement, and contact details.

    State machine (`tenure_status`):
      candidate → pre_hire → active ↔ on_leave
                              ↓
                       pre_offboarding → offboarded → archived_legal

    Privacy: columns are classified into four layers; the response
    serializer in the service layer masks fields based on caller role.
    """

    __tablename__ = "employee_profiles"

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

    # 1:1 with Member. UNIQUE enforces "one EmployeeProfile per Member".
    member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
        info={"privacy": PRIVACY_PUBLIC},
    )

    employee_no: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        info={"privacy": PRIVACY_HR_ONLY},
    )

    title: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        info={"privacy": PRIVACY_PUBLIC},
    )

    org_unit_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("org_units.uuid"),
        nullable=True,
        info={"privacy": PRIVACY_PUBLIC},
    )

    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(
            EmploymentType,
            name="employment_type",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        info={"privacy": PRIVACY_HR_ONLY},
    )

    hired_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        info={"privacy": PRIVACY_PUBLIC},
    )

    manager_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
        info={"privacy": PRIVACY_PUBLIC},
    )

    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        info={"privacy": PRIVACY_HR_ONLY},
    )

    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        info={"privacy": PRIVACY_HR_ONLY},
    )

    tenure_status: Mapped[TenureStatus] = mapped_column(
        Enum(
            TenureStatus,
            name="tenure_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=TenureStatus.CANDIDATE,
        nullable=False,
        info={"privacy": PRIVACY_PUBLIC},
    )

    leave_balance_days: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        info={"privacy": PRIVACY_MANAGER},
    )

    # Phase 3 (4대 보험 동의)
    insurance_consent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        info={"privacy": PRIVACY_HR_ONLY},
    )

    # Phase 2 — set by `documents.contract.signed` event subscriber.
    contract_signed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        info={"privacy": PRIVACY_HR_ONLY},
    )

    # Set on transition to OFFBOARDED. After this passes, hard-deletion is
    # allowed (Tier-aware retention job, Phase 3).
    data_retention_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        info={"privacy": PRIVACY_HR_ONLY},
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
            "member_uuid",
            name="uq_employee_profiles_workspace_member",
        ),
        Index(
            "idx_employee_profiles_workspace_tenure",
            "workspace_uuid",
            "tenure_status",
        ),
        Index(
            "idx_employee_profiles_workspace_org_unit",
            "workspace_uuid",
            "org_unit_uuid",
        ),
        Index(
            "idx_employee_profiles_workspace_manager",
            "workspace_uuid",
            "manager_member_uuid",
        ),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_active_employee(self) -> bool:
        return self.tenure_status == TenureStatus.ACTIVE


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------


class OnboardingPhase(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OnboardingWorkflow(Base, AutoUUIDMixin):
    """A new hire's onboarding checklist + automation tracker."""

    __tablename__ = "onboarding_workflows"

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
    target_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )
    # Template entity lands later (Phase 2 P1). Column-only FK for now.
    template_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    phase: Mapped[OnboardingPhase] = mapped_column(
        Enum(
            OnboardingPhase,
            name="onboarding_phase",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OnboardingPhase.PENDING,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    progress_pct: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    assigned_buddy_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
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
            "idx_onboarding_workflows_workspace_phase",
            "workspace_uuid",
            "phase",
        ),
        Index(
            "idx_onboarding_workflows_workspace_target",
            "workspace_uuid",
            "target_member_uuid",
        ),
    )


class OnboardingStepKind(enum.Enum):
    ACCOUNT_PROVISION = "account_provision"
    CHANNEL_JOIN = "channel_join"
    EQUIPMENT = "equipment"
    DOCUMENT_SIGN = "document_sign"
    TRAINING = "training"
    KPI_SETUP = "kpi_setup"


class OnboardingStepStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"


class OnboardingTargetDomain(enum.Enum):
    PM = "pm"
    COMMS = "comms"
    DOCUMENTS = "documents"


class OnboardingStep(Base, AutoUUIDMixin):
    """One actionable item inside an OnboardingWorkflow.

    `target_payload` carries the per-kind contract (e.g. channel_uuid for
    `channel_join`, document_template_uuid for `document_sign`). Schema is
    enforced at the service layer, not in the DB (JSONB allowed since the
    payload shape varies by kind).
    """

    __tablename__ = "onboarding_steps"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )
    workflow_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("onboarding_workflows.uuid", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.uuid"),
        nullable=False,
    )
    kind: Mapped[OnboardingStepKind] = mapped_column(
        Enum(
            OnboardingStepKind,
            name="onboarding_step_kind",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    target_domain: Mapped[OnboardingTargetDomain | None] = mapped_column(
        Enum(
            OnboardingTargetDomain,
            name="onboarding_target_domain",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    target_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    status: Mapped[OnboardingStepStatus] = mapped_column(
        Enum(
            OnboardingStepStatus,
            name="onboarding_step_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OnboardingStepStatus.PENDING,
        nullable=False,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    responsible_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
    )
    # `order` is a SQL reserved word; use `step_order` at the DB level.
    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
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
            "idx_onboarding_steps_workflow_order",
            "workflow_uuid",
            "step_order",
        ),
        Index(
            "idx_onboarding_steps_workspace_status",
            "workspace_uuid",
            "status",
        ),
    )


# ---------------------------------------------------------------------------
# Offboarding
# ---------------------------------------------------------------------------


class OffboardingReasonCode(enum.Enum):
    RESIGNATION = "resignation"
    AGREED_TERMINATION = "agreed_termination"
    DISMISSAL = "dismissal"
    CONTRACT_END = "contract_end"
    RETIREMENT = "retirement"


class OffboardingPhase(enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"  # 노무사 검토 진행 중
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class OffboardingFinalPaymentStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PAID = "paid"


class OffboardingWorkflow(Base, AutoUUIDMixin):
    """Offboarding tracker. Sensitive `reason_code` values
    (`agreed_termination`, `dismissal`) auto-queue 노무사 review.
    """

    __tablename__ = "offboarding_workflows"

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
    target_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )
    reason_code: Mapped[OffboardingReasonCode] = mapped_column(
        Enum(
            OffboardingReasonCode,
            name="offboarding_reason_code",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    requires_labor_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    phase: Mapped[OffboardingPhase] = mapped_column(
        Enum(
            OffboardingPhase,
            name="offboarding_phase",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OffboardingPhase.DRAFT,
        nullable=False,
    )
    final_payment_status: Mapped[OffboardingFinalPaymentStatus | None] = mapped_column(
        Enum(
            OffboardingFinalPaymentStatus,
            name="offboarding_final_payment_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    # Tier-specific retention applied after `effective_date`. Free text so
    # policy strings stay flexible until the retention engine lands (Phase 3).
    data_retention_policy: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        server_default=text("'default'"),
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
            "idx_offboarding_workflows_workspace_target",
            "workspace_uuid",
            "target_member_uuid",
        ),
        # Partial: queue of items awaiting 노무사 review.
        Index(
            "idx_offboarding_workflows_requires_labor_review",
            "workspace_uuid",
            postgresql_where=text("requires_labor_review = true"),
        ),
    )


# ---------------------------------------------------------------------------
# OneOnOne
# ---------------------------------------------------------------------------


class OneOnOneVisibility(enum.Enum):
    MANAGER_AND_REPORT = "manager_and_report"
    REPORT_ONLY_AFTER_SESSION = "report_only_after_session"


class OneOnOne(Base, AutoUUIDMixin):
    """Manager ↔ direct-report 1:1 notes — HR-only domain.

    Read/write are restricted to the two participants. Admin/Owner CANNOT
    read by default; the RLS policy `rls_one_on_ones_participant_only`
    (lands in a follow-up migration) enforces this at the DB level. Audit
    mode requires both-parties consent and is logged in `audit_logs`.
    """

    __tablename__ = "one_on_ones"

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
    manager_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )
    report_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    held_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notes_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_items: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    mood: Mapped[str | None] = mapped_column(String(32), nullable=True)  # Phase 3
    visibility: Mapped[OneOnOneVisibility] = mapped_column(
        Enum(
            OneOnOneVisibility,
            name="one_on_one_visibility",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OneOnOneVisibility.MANAGER_AND_REPORT,
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
            "idx_one_on_ones_workspace_manager_report_scheduled",
            "workspace_uuid",
            "manager_member_uuid",
            "report_member_uuid",
            "scheduled_at",
        ),
    )


# ---------------------------------------------------------------------------
# LeaveRequest
# ---------------------------------------------------------------------------


class LeaveType(enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    FAMILY = "family"
    COMPENSATORY = "compensatory"
    PUBLIC = "public"
    PARENTAL = "parental"
    MATERNITY = "maternity"


class LeaveStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONSUMED = "consumed"  # 사용 완료
    CANCELLED = "cancelled"


class LeaveRequest(Base, AutoUUIDMixin):
    """Leave application — annual / sick / family / etc."""

    __tablename__ = "leave_requests"

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
    requester_member_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=False,
    )
    leave_type: Mapped[LeaveType] = mapped_column(
        Enum(
            LeaveType,
            name="leave_type",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    half_day: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
    )
    reason_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    # File attachment metadata (Documents links). [{"uri":..., "kind":...}, ...]
    attachments: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(
            LeaveStatus,
            name="leave_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=LeaveStatus.DRAFT,
        nullable=False,
    )
    approver_member_uuid: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.uuid"),
        nullable=True,
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
            "idx_leave_requests_workspace_requester_status_dates",
            "workspace_uuid",
            "requester_member_uuid",
            "status",
            "start_date",
        ),
    )
