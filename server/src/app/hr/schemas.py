"""Pydantic Input / Output schemas for HR service functions.

Per docs/04-architecture/a2ui-strategy.md "Schema-first": every service
function exposes Pydantic schemas so it can be lifted into the A2UI Tool
Registry without rework.

The output schema's privacy-classified fields are all `Optional` because
the service-layer masker returns `None` for fields the caller cannot see
(docs/02-product/domain-hr.md "프라이버시 4계층").
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .model import EmploymentType, TenureStatus


class EmployeeProfileCreateInput(BaseModel):
    """HR Admin onboards a Member: links the EmployeeProfile and sets
    employment-type / org placement. Other PII (phone, birth_date) is
    captured later via update."""

    member_uuid: str
    employment_type: EmploymentType
    employee_no: str | None = Field(default=None, max_length=32)
    title: str | None = Field(default=None, max_length=100)
    org_unit_uuid: str | None = None
    hired_at: date | None = None
    manager_member_uuid: str | None = None


class EmployeeProfileUpdateInput(BaseModel):
    """Partial update; unset fields are not touched. `tenure_status`
    changes go through `transition_tenure_status` (state-machine guard).
    """

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
    """Privacy-masked. Fields the caller cannot see come back as `None`
    even if the underlying column is NOT NULL.
    """

    model_config = ConfigDict(from_attributes=False)

    uuid: str
    workspace_uuid: str
    member_uuid: str
    # Public layer — always present
    title: str | None = None
    org_unit_uuid: str | None = None
    hired_at: date | None = None
    manager_member_uuid: str | None = None
    tenure_status: TenureStatus
    # Manager-visible
    leave_balance_days: Decimal | None = None
    # HR-only
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
