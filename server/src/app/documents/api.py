"""Documents HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.deps import get_caller_member
from ..core.shared import Member
from .schemas import (
    DocumentInstanceDraftInput,
    DocumentInstanceListFilter,
    DocumentInstanceListOutput,
    DocumentInstanceOutput,
    DocumentInstanceVoidInput,
    DocumentTemplateCreateInput,
    DocumentTemplateListFilter,
    DocumentTemplateListOutput,
    DocumentTemplateOutput,
    RetentionPolicyCreateInput,
    RetentionPolicyListOutput,
    RetentionPolicyOutput,
)
from .service import (
    approve_document_instance,
    create_document_template,
    create_retention_policy,
    deprecate_document_template,
    draft_document_instance,
    get_document_instance,
    get_document_template,
    issue_document_instance,
    list_document_instances,
    list_document_templates,
    list_retention_policies,
    publish_document_template,
    reject_document_instance,
    submit_for_review,
    void_document_instance,
)

router = APIRouter(
    prefix="/workspaces/{workspace_uuid}/documents",
    tags=["documents"],
)


# ---------------------------------------------------------------------------
# RetentionPolicy
# ---------------------------------------------------------------------------


@router.post(
    "/retention-policies",
    response_model=RetentionPolicyOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_retention_policy_endpoint(
    payload: RetentionPolicyCreateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> RetentionPolicyOutput:
    return await create_retention_policy(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/retention-policies", response_model=RetentionPolicyListOutput)
async def list_retention_policies_endpoint(
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> RetentionPolicyListOutput:
    return await list_retention_policies(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        db=db,
    )


# ---------------------------------------------------------------------------
# DocumentTemplate
# ---------------------------------------------------------------------------


@router.post(
    "/templates",
    response_model=DocumentTemplateOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_template_endpoint(
    payload: DocumentTemplateCreateInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentTemplateOutput:
    return await create_document_template(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/templates", response_model=DocumentTemplateListOutput)
async def list_templates_endpoint(
    workspace_uuid: str = Path(...),
    filters: DocumentTemplateListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentTemplateListOutput:
    return await list_document_templates(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.get("/templates/{template_uuid}", response_model=DocumentTemplateOutput)
async def get_template_endpoint(
    template_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentTemplateOutput:
    return await get_document_template(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        template_uuid=template_uuid,
        db=db,
    )


@router.post(
    "/templates/{template_uuid}/publish",
    response_model=DocumentTemplateOutput,
)
async def publish_template_endpoint(
    template_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentTemplateOutput:
    return await publish_document_template(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        template_uuid=template_uuid,
        db=db,
    )


@router.post(
    "/templates/{template_uuid}/deprecate",
    response_model=DocumentTemplateOutput,
)
async def deprecate_template_endpoint(
    template_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentTemplateOutput:
    return await deprecate_document_template(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        template_uuid=template_uuid,
        db=db,
    )


# ---------------------------------------------------------------------------
# DocumentInstance
# ---------------------------------------------------------------------------


@router.post(
    "/instances",
    response_model=DocumentInstanceOutput,
    status_code=status.HTTP_201_CREATED,
)
async def draft_instance_endpoint(
    payload: DocumentInstanceDraftInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await draft_document_instance(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        payload=payload,
        db=db,
    )


@router.get("/instances", response_model=DocumentInstanceListOutput)
async def list_instances_endpoint(
    workspace_uuid: str = Path(...),
    filters: DocumentInstanceListFilter = Depends(),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceListOutput:
    return await list_document_instances(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        filters=filters,
        db=db,
    )


@router.get("/instances/{instance_uuid}", response_model=DocumentInstanceOutput)
async def get_instance_endpoint(
    instance_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await get_document_instance(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        instance_uuid=instance_uuid,
        db=db,
    )


@router.post(
    "/instances/{instance_uuid}/submit",
    response_model=DocumentInstanceOutput,
)
async def submit_instance_endpoint(
    instance_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await submit_for_review(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        instance_uuid=instance_uuid,
        db=db,
    )


@router.post(
    "/instances/{instance_uuid}/approve",
    response_model=DocumentInstanceOutput,
)
async def approve_instance_endpoint(
    instance_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await approve_document_instance(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        instance_uuid=instance_uuid,
        db=db,
    )


@router.post(
    "/instances/{instance_uuid}/reject",
    response_model=DocumentInstanceOutput,
)
async def reject_instance_endpoint(
    instance_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await reject_document_instance(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        instance_uuid=instance_uuid,
        db=db,
    )


@router.post(
    "/instances/{instance_uuid}/issue",
    response_model=DocumentInstanceOutput,
)
async def issue_instance_endpoint(
    instance_uuid: str,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await issue_document_instance(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        instance_uuid=instance_uuid,
        db=db,
    )


@router.post(
    "/instances/{instance_uuid}/void",
    response_model=DocumentInstanceOutput,
)
async def void_instance_endpoint(
    instance_uuid: str,
    payload: DocumentInstanceVoidInput,
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> DocumentInstanceOutput:
    return await void_document_instance(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        instance_uuid=instance_uuid,
        payload=payload,
        db=db,
    )
