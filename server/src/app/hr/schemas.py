"""Pydantic Input / Output schemas for HR service functions."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .model import (
    EmploymentType,
    LeaveStatus,
    LeaveType,
    OffboardingFinalPaymentStatus,
    OffboardingPhase,
    OffboardingReasonCode,
    OnboardingPhase,
    OnboardingStepKind,
    OnboardingStepStatus,
    OnboardingTargetDomain,
    OneOnOneVisibility,
    TenureStatus,
)

# ---------------------------------------------------------------------------
# EmployeeProfile
# ---------------------------------------------------------------------------


class EmployeeProfileCreateInput(BaseModel):
    member_uuid: str
    employment_type: EmploymentType
    employee_no: str | None = Field(default=None, max_length=32)
    title: str | None = Field(default=None, max_length=100)
    org_unit_uuid: str | None = None
    hired_at: date | None = None
    manager_member_uuid: str | None = None


class EmployeeProfileUpdateInput(BaseModel):
    employee_no: str | None = Field(default=None, max_length=32)
    title: str | None = Field(default=None, max_length=100)
    org_unit_uuid: str | None = None
    employment_type: EmploymentType | None = None
    hired_at: date | None = None
    manager_member_uuid: str | None = None
    birth_date: date | None = None
    phone: str | None = Field(default=None, max_length=32)
    leave_balance_days: Decimal | None = None


class TenureTransitionInput(BaseModel):
    new_status: TenureStatus


class EmployeeProfileListFilter(BaseModel):
    tenure_status: TenureStatus | None = None
    org_unit_uuid: str | None = None
    manager_member_uuid: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class EmployeeProfileOutput(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    uuid: str
    workspace_uuid: str
    member_uuid: str
    title: str | None = None
    org_unit_uuid: str | None = None
    hired_at: date | None = None
    manager_member_uuid: str | None = None
    tenure_status: TenureStatus
    leave_balance_days: Decimal | None = None
    employee_no: str | None = None
    employment_type: EmploymentType | None = None
    birth_date: date | None = None
    phone: str | None = None
    insurance_consent_at: datetime | None = None
    contract_signed_at: datetime | None = None
    data_retention_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class EmployeeProfileListOutput(BaseModel):
    profiles: list[EmployeeProfileOutput]
    total: int


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------


class OnboardingStepSeed(BaseModel):
    kind: OnboardingStepKind
    target_domain: OnboardingTargetDomain | None = None
    target_payload: dict[str, Any] = Field(default_factory=dict)
    due_date: date | None = None
    responsible_member_uuid: str | None = None
    step_order: int = 0


class OnboardingStartInput(BaseModel):
    target_member_uuid: str
    template_uuid: str | None = None
    assigned_buddy_member_uuid: str | None = None
    steps: list[OnboardingStepSeed] = Field(default_factory=list)


class OnboardingStepOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workflow_uuid: str
    workspace_uuid: str
    kind: OnboardingStepKind
    target_domain: OnboardingTargetDomain | None
    target_payload: dict[str, Any]
    status: OnboardingStepStatus
    due_date: date | None
    responsible_member_uuid: str | None
    step_order: int
    created_at: datetime
    updated_at: datetime


class OnboardingWorkflowOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    target_member_uuid: str
    template_uuid: str | None
    phase: OnboardingPhase
    started_at: datetime | None
    completed_at: datetime | None
    progress_pct: int
    assigned_buddy_member_uuid: str | None
    created_at: datetime
    updated_at: datetime


class OnboardingWorkflowWithStepsOutput(OnboardingWorkflowOutput):
    steps: list[OnboardingStepOutput]


class OnboardingListFilter(BaseModel):
    phase: OnboardingPhase | None = None
    target_member_uuid: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class OnboardingListOutput(BaseModel):
    workflows: list[OnboardingWorkflowOutput]
    total: int


# ---------------------------------------------------------------------------
# Offboarding
# ---------------------------------------------------------------------------


_SENSITIVE_OFFBOARDING_REASONS = frozenset(
    {OffboardingReasonCode.AGREED_TERMINATION, OffboardingReasonCode.DISMISSAL}
)


class OffboardingStartInput(BaseModel):
    target_member_uuid: str
    reason_code: OffboardingReasonCode
    effective_date: date
    data_retention_policy: str = "default"


class OffboardingTransitionInput(BaseModel):
    new_phase: OffboardingPhase
    final_payment_status: OffboardingFinalPaymentStatus | None = None


class OffboardingOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    target_member_uuid: str
    reason_code: OffboardingReasonCode
    requires_labor_review: bool
    effective_date: date
    phase: OffboardingPhase
    final_payment_status: OffboardingFinalPaymentStatus | None
    data_retention_policy: str
    created_at: datetime
    updated_at: datetime


class OffboardingListFilter(BaseModel):
    phase: OffboardingPhase | None = None
    requires_labor_review: bool | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class OffboardingListOutput(BaseModel):
    workflows: list[OffboardingOutput]
    total: int


# ---------------------------------------------------------------------------
# OneOnOne
# ---------------------------------------------------------------------------


class OneOnOneCreateInput(BaseModel):
    """Only the manager schedules. `manager_member_uuid` is inferred from
    the caller — clients pass `report_member_uuid` + `scheduled_at` only.
    """

    report_member_uuid: str
    scheduled_at: datetime
    visibility: OneOnOneVisibility = OneOnOneVisibility.MANAGER_AND_REPORT


class OneOnOneEditInput(BaseModel):
    held_at: datetime | None = None
    notes_md: str | None = None
    action_items: list[dict[str, Any]] | None = None
    mood: str | None = Field(default=None, max_length=32)


class OneOnOneOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    manager_member_uuid: str
    report_member_uuid: str
    scheduled_at: datetime
    held_at: datetime | None
    notes_md: str | None
    action_items: list[dict[str, Any]]
    mood: str | None
    visibility: OneOnOneVisibility
    created_at: datetime
    updated_at: datetime


class OneOnOneListFilter(BaseModel):
    """Caller-scoped: returns 1:1s where caller is manager OR report."""

    other_party_member_uuid: str | None = None  # narrow to a specific pair
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class OneOnOneListOutput(BaseModel):
    one_on_ones: list[OneOnOneOutput]
    total: int


# ---------------------------------------------------------------------------
# LeaveRequest
# ---------------------------------------------------------------------------


class LeaveSubmitInput(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    half_day: bool = False
    reason_md: str | None = None
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class LeaveDecisionInput(BaseModel):
    """Approve or reject; `status` must be APPROVED or REJECTED."""

    status: LeaveStatus


class LeaveOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    requester_member_uuid: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    half_day: bool
    reason_md: str | None
    attachments: list[dict[str, Any]]
    status: LeaveStatus
    approver_member_uuid: str | None
    created_at: datetime
    updated_at: datetime


class LeaveListFilter(BaseModel):
    requester_member_uuid: str | None = None  # default: caller's own
    status: LeaveStatus | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class LeaveListOutput(BaseModel):
    leaves: list[LeaveOutput]
    total: int
