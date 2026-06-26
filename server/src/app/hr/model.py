from __future__ import annotations

import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
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
