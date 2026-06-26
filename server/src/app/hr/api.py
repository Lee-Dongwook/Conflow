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
    TenureTransitionInput,
)
from .service import (
    create_employee_profile,
    get_employee_profile,
    list_employee_profiles,
    transition_tenure_status,
    update_employee_profile,
)

router = APIRouter(
    prefix="/workspaces/{workspace_uuid}/hr/profiles",
    tags=["hr"],
)


@router.post(
    "",
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


@router.get("", response_model=EmployeeProfileListOutput)
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


@router.get("/{profile_uuid}", response_model=EmployeeProfileOutput)
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


@router.patch("/{profile_uuid}", response_model=EmployeeProfileOutput)
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
    "/{profile_uuid}/transition",
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
