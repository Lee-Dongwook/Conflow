"""HR domain — EmployeeProfile, OrgUnit, Onboarding/Offboarding, 1:1, Leave.

Owns the personnel side of `Member`. Document issuance (employment
contracts, payroll PDFs) belongs to the Documents domain — HR provides
the data, Documents renders and signs (docs/02-product/domain-overview.md).
"""

from .model import (
    EmployeeProfile,
    EmploymentType,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
    OffboardingFinalPaymentStatus,
    OffboardingPhase,
    OffboardingReasonCode,
    OffboardingWorkflow,
    OnboardingPhase,
    OnboardingStep,
    OnboardingStepKind,
    OnboardingStepStatus,
    OnboardingTargetDomain,
    OnboardingWorkflow,
    OneOnOne,
    OneOnOneVisibility,
    OrgUnit,
    OrgUnitKind,
    TenureStatus,
)

__all__ = [
    "EmployeeProfile",
    "EmploymentType",
    "LeaveRequest",
    "LeaveStatus",
    "LeaveType",
    "OffboardingFinalPaymentStatus",
    "OffboardingPhase",
    "OffboardingReasonCode",
    "OffboardingWorkflow",
    "OnboardingPhase",
    "OnboardingStep",
    "OnboardingStepKind",
    "OnboardingStepStatus",
    "OnboardingTargetDomain",
    "OnboardingWorkflow",
    "OneOnOne",
    "OneOnOneVisibility",
    "OrgUnit",
    "OrgUnitKind",
    "TenureStatus",
]
