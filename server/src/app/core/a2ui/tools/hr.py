"""HR domain Tools — register at import.

`hr.get_member_context` is marked `cross_domain=True` because it joins
the Shared Core `Member` + HR `EmployeeProfile` to give a single context
view; the response is privacy-masked per caller role by the underlying
HR service.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....hr.model import EmployeeProfile
from ....hr.schemas import (
    EmployeeProfileOutput,
    OnboardingListFilter,
    OnboardingListOutput,
)
from ....hr.service import get_employee_profile, list_onboardings
from ...shared import WorkspaceTier
from ..registry import PermissionLevel, ToolSpec, register_tool


class HrGetMemberContextInput(BaseModel):
    member_uuid: str = Field(description="Member UUID to fetch HR context for")


async def _hr_get_member_context(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: HrGetMemberContextInput,
    db: AsyncSession,
) -> EmployeeProfileOutput:
    # Resolve EmployeeProfile by member_uuid (the natural cross-domain key).
    res = await db.execute(
        select(EmployeeProfile.uuid).where(
            EmployeeProfile.workspace_uuid == workspace_uuid,
            EmployeeProfile.member_uuid == payload.member_uuid,
            EmployeeProfile.deleted_at.is_(None),
        )
    )
    profile_uuid = res.scalar_one_or_none()
    if profile_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No EmployeeProfile exists for this Member",
        )
    return await get_employee_profile(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        profile_uuid=profile_uuid,
        db=db,
    )


register_tool(
    ToolSpec(
        id="hr.get_member_context",
        domain="hr",
        description=(
            "Fetch an HR-shaped view of a Member: title, org, hire date, "
            "manager, tenure status. Privacy-masked per caller role "
            "(public / manager_visible / hr_only / self_only)."
        ),
        handler=_hr_get_member_context,
        input_schema=HrGetMemberContextInput,
        output_schema=EmployeeProfileOutput,
        min_tier=WorkspaceTier.BUSINESS,
        permission_required=PermissionLevel.MEMBER,
        cross_domain=True,
        phase=2,
    )
)


async def _hr_list_onboarding(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: OnboardingListFilter,
    db: AsyncSession,
) -> OnboardingListOutput:
    return await list_onboardings(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        filters=payload,
        db=db,
    )


register_tool(
    ToolSpec(
        id="hr.list_onboarding",
        domain="hr",
        description=(
            "List onboarding workflows with optional phase / target_member "
            "filter. Returns workflow headers only (no step details)."
        ),
        handler=_hr_list_onboarding,
        input_schema=OnboardingListFilter,
        output_schema=OnboardingListOutput,
        min_tier=WorkspaceTier.BUSINESS,
        permission_required=PermissionLevel.MEMBER,
        phase=2,
    )
)
