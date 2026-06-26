"""HR HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.deps import get_caller_member
from ..core.shared import Member
from .schemas import (
    EmployeeProfileCreateInput,
    EmployeeProfileListFilter,
    EmployeeProfileListOutput,
    EmployeeProfileOutput,
    EmployeeProfileUpdateInput,
    LeaveDecisionInput,
    LeaveListFilter,
    LeaveListOutput,
    LeaveOutput,
    LeaveSubmitInput,
    OffboardingListFilter,
    OffboardingListOutput,
    OffboardingOutput,
    OffboardingStartInput,
    OffboardingTransitionInput,
    OnboardingListFilter,
    OnboardingListOutput,
    OnboardingStartInput,
    OnboardingStepOutput,
    OnboardingWorkflowWithStepsOutput,
    OneOnOneCreateInput,
    OneOnOneEditInput,
    OneOnOneListFilter,
    OneOnOneListOutput,
    OneOnOneOutput,
    TenureTransitionInput,
)
from .service import (
    create_employee_profile,
    create_one_on_one,
    decide_leave,
    edit_one_on_one,
    get_employee_profile,
    get_onboarding_with_steps,
    list_employee_profiles,
    list_leaves,
    list_my_one_on_ones,
    list_offboardings,
    list_onboardings,
    mark_step_done,
    start_offboarding,
    start_onboarding,
    submit_leave,
    transition_offboarding_phase,
    transition_tenure_status,
    update_employee_profile,
)

router = APIRouter(prefix="/workspaces/{workspace_uuid}/hr", tags=["hr"])


# ---------------------------------------------------------------------------
# EmployeeProfile
# ---------------------------------------------------------------------------


@router.post(
    "/profiles",
    response_model=EmployeeProfileOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee_profile_endpoint(
    payload: EmployeeProfileCreateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> EmployeeProfileOutput:
    return await create_employee_profile(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/profiles", response_model=EmployeeProfileListOutput)
async def list_employee_profiles_endpoint(
    workspace_uuid: str = Path(...),
    filters: EmployeeProfileListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> EmployeeProfileListOutput:
    return await list_employee_profiles(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.get("/profiles/{profile_uuid}", response_model=EmployeeProfileOutput)
async def get_employee_profile_endpoint(
    profile_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> EmployeeProfileOutput:
    return await get_employee_profile(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        profile_uuid=profile_uuid,
        db=db,
    )


@router.patch("/profiles/{profile_uuid}", response_model=EmployeeProfileOutput)
async def update_employee_profile_endpoint(
    profile_uuid: str,
    payload: EmployeeProfileUpdateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> EmployeeProfileOutput:
    return await update_employee_profile(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        profile_uuid=profile_uuid,
        payload=payload,
        db=db,
    )


@router.post(
    "/profiles/{profile_uuid}/transition",
    response_model=EmployeeProfileOutput,
)
async def transition_tenure_endpoint(
    profile_uuid: str,
    payload: TenureTransitionInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> EmployeeProfileOutput:
    return await transition_tenure_status(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        profile_uuid=profile_uuid,
        payload=payload,
        db=db,
    )


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------


@router.post(
    "/onboardings",
    response_model=OnboardingWorkflowWithStepsOutput,
    status_code=status.HTTP_201_CREATED,
)
async def start_onboarding_endpoint(
    payload: OnboardingStartInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OnboardingWorkflowWithStepsOutput:
    return await start_onboarding(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/onboardings", response_model=OnboardingListOutput)
async def list_onboardings_endpoint(
    workspace_uuid: str = Path(...),
    filters: OnboardingListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OnboardingListOutput:
    return await list_onboardings(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.get(
    "/onboardings/{workflow_uuid}",
    response_model=OnboardingWorkflowWithStepsOutput,
)
async def get_onboarding_endpoint(
    workflow_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OnboardingWorkflowWithStepsOutput:
    return await get_onboarding_with_steps(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        workflow_uuid=workflow_uuid,
        db=db,
    )


@router.post(
    "/onboarding-steps/{step_uuid}/done",
    response_model=OnboardingStepOutput,
)
async def mark_step_done_endpoint(
    step_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OnboardingStepOutput:
    return await mark_step_done(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        step_uuid=step_uuid,
        db=db,
    )


# ---------------------------------------------------------------------------
# Offboarding
# ---------------------------------------------------------------------------


@router.post(
    "/offboardings",
    response_model=OffboardingOutput,
    status_code=status.HTTP_201_CREATED,
)
async def start_offboarding_endpoint(
    payload: OffboardingStartInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OffboardingOutput:
    return await start_offboarding(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/offboardings", response_model=OffboardingListOutput)
async def list_offboardings_endpoint(
    workspace_uuid: str = Path(...),
    filters: OffboardingListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OffboardingListOutput:
    return await list_offboardings(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.post(
    "/offboardings/{workflow_uuid}/transition",
    response_model=OffboardingOutput,
)
async def transition_offboarding_endpoint(
    workflow_uuid: str,
    payload: OffboardingTransitionInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OffboardingOutput:
    return await transition_offboarding_phase(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        workflow_uuid=workflow_uuid,
        payload=payload,
        db=db,
    )


# ---------------------------------------------------------------------------
# OneOnOne
# ---------------------------------------------------------------------------


@router.post(
    "/one-on-ones",
    response_model=OneOnOneOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_one_on_one_endpoint(
    payload: OneOnOneCreateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OneOnOneOutput:
    return await create_one_on_one(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/one-on-ones", response_model=OneOnOneListOutput)
async def list_one_on_ones_endpoint(
    workspace_uuid: str = Path(...),
    filters: OneOnOneListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OneOnOneListOutput:
    return await list_my_one_on_ones(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.patch("/one-on-ones/{one_on_one_uuid}", response_model=OneOnOneOutput)
async def edit_one_on_one_endpoint(
    one_on_one_uuid: str,
    payload: OneOnOneEditInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> OneOnOneOutput:
    return await edit_one_on_one(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        one_on_one_uuid=one_on_one_uuid,
        payload=payload,
        db=db,
    )


# ---------------------------------------------------------------------------
# LeaveRequest
# ---------------------------------------------------------------------------


@router.post(
    "/leaves",
    response_model=LeaveOutput,
    status_code=status.HTTP_201_CREATED,
)
async def submit_leave_endpoint(
    payload: LeaveSubmitInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> LeaveOutput:
    return await submit_leave(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/leaves", response_model=LeaveListOutput)
async def list_leaves_endpoint(
    workspace_uuid: str = Path(...),
    filters: LeaveListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> LeaveListOutput:
    return await list_leaves(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.post("/leaves/{leave_uuid}/decide", response_model=LeaveOutput)
async def decide_leave_endpoint(
    leave_uuid: str,
    payload: LeaveDecisionInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> LeaveOutput:
    return await decide_leave(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        leave_uuid=leave_uuid,
        payload=payload,
        db=db,
    )
