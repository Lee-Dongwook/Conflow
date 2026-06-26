"""Headless Documents service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments and returns Pydantic models (docs/04-architecture/a2ui-strategy.md).

State machine for `DocumentInstance` (subset shipped in alpha):
    draft → pending_review → approved → issued → archived
                          ↓
                       rejected (back to draft)
    Any non-terminal state → void (with reason).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.events import (
    DOCUMENTS_CONTRACT_SIGNED,
    DOCUMENTS_INSTANCE_ISSUED,
    DOCUMENTS_INSTANCE_VOIDED,
    emit_event,
)
from ..core.permissions import (
    PermissionDenied,
    is_workspace_admin,
    require_workspace_admin,
    require_workspace_member,
    require_workspace_writer,
)
from ..core.shared import AuditDomain, AuditLog
from .model import (
    DocumentInstance,
    DocumentInstanceState,
    DocumentTemplate,
    RetentionPolicy,
    ReviewWorkflow,
    ReviewWorkflowState,
    TemplateState,
)
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
    ReviewWorkflowOutput,
)

# State machine: alpha subset.
_VALID_INSTANCE_TRANSITIONS: dict[
    DocumentInstanceState, set[DocumentInstanceState]
] = {
    DocumentInstanceState.DRAFT: {
        DocumentInstanceState.PENDING_REVIEW,
        DocumentInstanceState.VOID,
    },
    DocumentInstanceState.PENDING_REVIEW: {
        DocumentInstanceState.APPROVED,
        DocumentInstanceState.DRAFT,  # reject → back to draft
        DocumentInstanceState.VOID,
    },
    DocumentInstanceState.APPROVED: {
        DocumentInstanceState.ISSUED,
        DocumentInstanceState.SIGNED,  # Phase 4 KISA path
        DocumentInstanceState.VOID,
    },
    DocumentInstanceState.SIGNED: {DocumentInstanceState.ISSUED},
    DocumentInstanceState.ISSUED: {DocumentInstanceState.ARCHIVED},
    DocumentInstanceState.ARCHIVED: {
        DocumentInstanceState.ARCHIVED_LEGAL_ONLY,
    },
    DocumentInstanceState.ARCHIVED_LEGAL_ONLY: set(),
    DocumentInstanceState.VOID: set(),
}

# Subtypes whose `documents.instance.issued` ALSO fires the
# specialized `documents.contract.signed` event (HR subscribers consume).
_CONTRACT_SUBTYPES: frozenset[str] = frozenset(
    {"employment_contract", "labor_contract"}
)


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _audit(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    actor_member_uuid: str | None,
    action: str,
    resource_type: str,
    resource_uuid: str,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=actor_member_uuid,
            domain=AuditDomain.DOCUMENTS,
            action=action,
            resource_type=resource_type,
            resource_uuid=resource_uuid,
            audit_metadata=metadata or {},
        )
    )


# ---------------------------------------------------------------------------
# RetentionPolicy
# ---------------------------------------------------------------------------


async def create_retention_policy(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: RetentionPolicyCreateInput,
    db: AsyncSession,
) -> RetentionPolicyOutput:
    """HR Admin (== Workspace Admin in alpha) only."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    policy = RetentionPolicy(
        workspace_uuid=workspace_uuid,
        name=payload.name,
        retention_days=payload.retention_days,
        immutable=payload.immutable,
    )
    db.add(policy)
    await db.flush()
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.retention_policy.created",
        resource_type="documents.retention_policy",
        resource_uuid=policy.uuid,
        metadata={
            "name": payload.name,
            "retention_days": payload.retention_days,
            "immutable": payload.immutable,
        },
    )
    await db.commit()
    await db.refresh(policy)
    return RetentionPolicyOutput.model_validate(policy)


async def list_retention_policies(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    db: AsyncSession,
) -> RetentionPolicyListOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    res = await db.execute(
        select(RetentionPolicy)
        .where(
            RetentionPolicy.workspace_uuid == workspace_uuid,
            RetentionPolicy.deleted_at.is_(None),
        )
        .order_by(RetentionPolicy.created_at)
    )
    return RetentionPolicyListOutput(
        policies=[RetentionPolicyOutput.model_validate(p) for p in res.scalars().all()],
    )


# ---------------------------------------------------------------------------
# DocumentTemplate
# ---------------------------------------------------------------------------


async def create_document_template(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: DocumentTemplateCreateInput,
    db: AsyncSession,
) -> DocumentTemplateOutput:
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )

    # Verify retention policy belongs to this workspace.
    retention = await db.get(RetentionPolicy, payload.default_retention_policy_uuid)
    if retention is None or retention.workspace_uuid != workspace_uuid:
        raise _bad_request("default_retention_policy_uuid not in this workspace")

    template = DocumentTemplate(
        workspace_uuid=workspace_uuid,
        name=payload.name,
        category=payload.category,
        subtype=payload.subtype,
        body_md=payload.body_md,
        variables_schema=payload.variables_schema,
        default_retention_policy_uuid=payload.default_retention_policy_uuid,
        requires_signature=payload.requires_signature,
        version=payload.version,
        created_by_member_uuid=caller_member_uuid,
        state=TemplateState.DRAFT,
    )
    db.add(template)
    await db.flush()
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.template.created",
        resource_type="documents.template",
        resource_uuid=template.uuid,
        metadata={
            "name": payload.name,
            "category": payload.category.value,
            "subtype": payload.subtype,
        },
    )
    await db.commit()
    await db.refresh(template)
    return DocumentTemplateOutput.model_validate(template)


async def publish_document_template(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    template_uuid: str,
    db: AsyncSession,
) -> DocumentTemplateOutput:
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    template = await _get_template_or_404(
        db, workspace_uuid=workspace_uuid, template_uuid=template_uuid
    )
    if template.state == TemplateState.PUBLISHED:
        return DocumentTemplateOutput.model_validate(template)
    if template.state != TemplateState.DRAFT:
        raise _bad_request(f"Cannot publish from state {template.state.value}")
    template.state = TemplateState.PUBLISHED
    template.published_at = datetime.now(timezone.utc)  # noqa: UP017
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.template.published",
        resource_type="documents.template",
        resource_uuid=template.uuid,
    )
    await db.commit()
    await db.refresh(template)
    return DocumentTemplateOutput.model_validate(template)


async def deprecate_document_template(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    template_uuid: str,
    db: AsyncSession,
) -> DocumentTemplateOutput:
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    template = await _get_template_or_404(
        db, workspace_uuid=workspace_uuid, template_uuid=template_uuid
    )
    if template.state == TemplateState.DEPRECATED:
        return DocumentTemplateOutput.model_validate(template)
    template.state = TemplateState.DEPRECATED
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.template.deprecated",
        resource_type="documents.template",
        resource_uuid=template.uuid,
    )
    await db.commit()
    await db.refresh(template)
    return DocumentTemplateOutput.model_validate(template)


async def get_document_template(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    template_uuid: str,
    db: AsyncSession,
) -> DocumentTemplateOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    template = await _get_template_or_404(
        db, workspace_uuid=workspace_uuid, template_uuid=template_uuid
    )
    return DocumentTemplateOutput.model_validate(template)


async def list_document_templates(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: DocumentTemplateListFilter,
    db: AsyncSession,
) -> DocumentTemplateListOutput:
    await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    base = select(DocumentTemplate).where(
        DocumentTemplate.workspace_uuid == workspace_uuid,
        DocumentTemplate.deleted_at.is_(None),
    )
    if filters.category is not None:
        base = base.where(DocumentTemplate.category == filters.category)
    if filters.state is not None:
        base = base.where(DocumentTemplate.state == filters.state)
    total = int(
        (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    )
    page = await db.execute(
        base.order_by(DocumentTemplate.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    return DocumentTemplateListOutput(
        templates=[
            DocumentTemplateOutput.model_validate(t) for t in page.scalars().all()
        ],
        total=total,
    )


async def _get_template_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    template_uuid: str,
) -> DocumentTemplate:
    res = await db.execute(
        select(DocumentTemplate).where(
            DocumentTemplate.uuid == template_uuid,
            DocumentTemplate.workspace_uuid == workspace_uuid,
            DocumentTemplate.deleted_at.is_(None),
        )
    )
    template = res.scalar_one_or_none()
    if template is None:
        raise _not_found("DocumentTemplate not found")
    return template


# ---------------------------------------------------------------------------
# DocumentInstance
# ---------------------------------------------------------------------------


async def _get_instance_or_404(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    instance_uuid: str,
) -> DocumentInstance:
    res = await db.execute(
        select(DocumentInstance).where(
            DocumentInstance.uuid == instance_uuid,
            DocumentInstance.workspace_uuid == workspace_uuid,
        )
    )
    instance = res.scalar_one_or_none()
    if instance is None:
        raise _not_found("DocumentInstance not found")
    return instance


def _compute_retention_expires_at(policy: RetentionPolicy) -> datetime | None:
    if policy.retention_days is None:
        return None
    return datetime.now(timezone.utc) + timedelta(days=policy.retention_days)  # noqa: UP017


async def draft_document_instance(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: DocumentInstanceDraftInput,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    """Create a draft instance from a published template. The variables
    snapshot freezes the rendering context — later template edits will not
    mutate this instance.
    """
    await require_workspace_writer(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    template = await _get_template_or_404(
        db, workspace_uuid=workspace_uuid, template_uuid=payload.template_uuid
    )
    if template.state != TemplateState.PUBLISHED:
        raise _bad_request("Template must be PUBLISHED to draft an instance")

    instance = DocumentInstance(
        workspace_uuid=workspace_uuid,
        template_uuid=template.uuid,
        template_version=template.version,
        subject_member_uuid=payload.subject_member_uuid,
        requester_member_uuid=caller_member_uuid,
        variables_snapshot=payload.variables_snapshot,
        retention_policy_uuid=template.default_retention_policy_uuid,
        state=DocumentInstanceState.DRAFT,
    )
    db.add(instance)
    await db.flush()
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.instance.drafted",
        resource_type="documents.instance",
        resource_uuid=instance.uuid,
        metadata={
            "template_uuid": template.uuid,
            "subject_member_uuid": payload.subject_member_uuid,
            "subtype": template.subtype,
        },
    )
    await db.commit()
    await db.refresh(instance)
    return DocumentInstanceOutput.model_validate(instance)


async def submit_for_review(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    instance_uuid: str,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    """DRAFT → PENDING_REVIEW. Creates a `ReviewWorkflow` aggregate row.
    Review-step seeding lands with the review-steps entity in a later step.
    """
    roles = await require_workspace_writer(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    instance = await _get_instance_or_404(
        db, workspace_uuid=workspace_uuid, instance_uuid=instance_uuid
    )
    if not (
        instance.requester_member_uuid == caller_member_uuid
        or is_workspace_admin(roles)
    ):
        raise PermissionDenied("Only the requester or Admin may submit")
    _assert_transition(instance.state, DocumentInstanceState.PENDING_REVIEW)

    workflow = ReviewWorkflow(
        workspace_uuid=workspace_uuid,
        instance_uuid=instance.uuid,
        state=ReviewWorkflowState.PENDING,
    )
    db.add(workflow)
    await db.flush()

    instance.state = DocumentInstanceState.PENDING_REVIEW
    instance.review_workflow_uuid = workflow.uuid
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.instance.submitted_for_review",
        resource_type="documents.instance",
        resource_uuid=instance.uuid,
        metadata={"review_workflow_uuid": workflow.uuid},
    )
    await db.commit()
    await db.refresh(instance)
    return DocumentInstanceOutput.model_validate(instance)


async def approve_document_instance(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    instance_uuid: str,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    """PENDING_REVIEW → APPROVED. Admin only in alpha (per-step reviewer
    matching lands with the review_steps entity)."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    instance = await _get_instance_or_404(
        db, workspace_uuid=workspace_uuid, instance_uuid=instance_uuid
    )
    _assert_transition(instance.state, DocumentInstanceState.APPROVED)
    instance.state = DocumentInstanceState.APPROVED
    if instance.review_workflow_uuid is not None:
        wf = await db.get(ReviewWorkflow, instance.review_workflow_uuid)
        if wf is not None:
            wf.state = ReviewWorkflowState.APPROVED
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.instance.approved",
        resource_type="documents.instance",
        resource_uuid=instance.uuid,
    )
    await db.commit()
    await db.refresh(instance)
    return DocumentInstanceOutput.model_validate(instance)


async def reject_document_instance(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    instance_uuid: str,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    """PENDING_REVIEW → DRAFT (rejection sends it back for edits)."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    instance = await _get_instance_or_404(
        db, workspace_uuid=workspace_uuid, instance_uuid=instance_uuid
    )
    _assert_transition(instance.state, DocumentInstanceState.DRAFT)
    instance.state = DocumentInstanceState.DRAFT
    if instance.review_workflow_uuid is not None:
        wf = await db.get(ReviewWorkflow, instance.review_workflow_uuid)
        if wf is not None:
            wf.state = ReviewWorkflowState.REJECTED
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.instance.rejected",
        resource_type="documents.instance",
        resource_uuid=instance.uuid,
    )
    await db.commit()
    await db.refresh(instance)
    return DocumentInstanceOutput.model_validate(instance)


async def issue_document_instance(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    instance_uuid: str,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    """APPROVED|SIGNED → ISSUED. Stamps `issued_at` + `retention_expires_at`
    + emits `documents.instance.issued`; if template subtype is in
    `_CONTRACT_SUBTYPES`, ALSO emits `documents.contract.signed` so the HR
    subscriber can stamp `EmployeeProfile.contract_signed_at`.
    """
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    instance = await _get_instance_or_404(
        db, workspace_uuid=workspace_uuid, instance_uuid=instance_uuid
    )
    _assert_transition(instance.state, DocumentInstanceState.ISSUED)

    retention = await db.get(RetentionPolicy, instance.retention_policy_uuid)
    if retention is None:
        raise _bad_request("Retention policy missing")

    instance.state = DocumentInstanceState.ISSUED
    instance.issued_at = datetime.now(timezone.utc)  # noqa: UP017
    instance.retention_expires_at = _compute_retention_expires_at(retention)

    template = await db.get(DocumentTemplate, instance.template_uuid)
    subtype = template.subtype if template is not None else None
    common_payload: dict[str, Any] = {
        "instance_uuid": instance.uuid,
        "template_uuid": instance.template_uuid,
        "template_version": instance.template_version,
        "subtype": subtype,
        "subject_member_uuid": instance.subject_member_uuid,
        "requester_member_uuid": instance.requester_member_uuid,
        "issued_at": instance.issued_at.isoformat(),
    }

    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.instance.issued",
        resource_type="documents.instance",
        resource_uuid=instance.uuid,
        metadata={"subtype": subtype},
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=DOCUMENTS_INSTANCE_ISSUED,
        payload=common_payload,
    )
    if subtype in _CONTRACT_SUBTYPES and instance.subject_member_uuid is not None:
        emit_event(
            db,
            workspace_uuid=workspace_uuid,
            event_name=DOCUMENTS_CONTRACT_SIGNED,
            payload=common_payload,
        )

    await db.commit()
    await db.refresh(instance)
    return DocumentInstanceOutput.model_validate(instance)


async def void_document_instance(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    instance_uuid: str,
    payload: DocumentInstanceVoidInput,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    """Any non-terminal state → VOID. Issued instances stay in the system
    (audit trail) but state is marked void with a reason."""
    await require_workspace_admin(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    instance = await _get_instance_or_404(
        db, workspace_uuid=workspace_uuid, instance_uuid=instance_uuid
    )
    _assert_transition(instance.state, DocumentInstanceState.VOID)
    instance.state = DocumentInstanceState.VOID
    instance.void_reason = payload.void_reason
    _audit(
        db,
        workspace_uuid=workspace_uuid,
        actor_member_uuid=caller_member_uuid,
        action="documents.instance.voided",
        resource_type="documents.instance",
        resource_uuid=instance.uuid,
        metadata={"reason": payload.void_reason},
    )
    emit_event(
        db,
        workspace_uuid=workspace_uuid,
        event_name=DOCUMENTS_INSTANCE_VOIDED,
        payload={
            "instance_uuid": instance.uuid,
            "reason": payload.void_reason,
        },
    )
    await db.commit()
    await db.refresh(instance)
    return DocumentInstanceOutput.model_validate(instance)


async def get_document_instance(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    instance_uuid: str,
    db: AsyncSession,
) -> DocumentInstanceOutput:
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    instance = await _get_instance_or_404(
        db, workspace_uuid=workspace_uuid, instance_uuid=instance_uuid
    )
    # Subject / requester / Admin may read.
    if not (
        instance.subject_member_uuid == caller_member_uuid
        or instance.requester_member_uuid == caller_member_uuid
        or is_workspace_admin(roles)
    ):
        raise PermissionDenied("Not authorized to read this instance")
    return DocumentInstanceOutput.model_validate(instance)


async def list_document_instances(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    filters: DocumentInstanceListFilter,
    db: AsyncSession,
) -> DocumentInstanceListOutput:
    """HR/Workspace Admin: list all. Non-admin: scope to own
    (requester OR subject) instances.
    """
    roles = await require_workspace_member(
        db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
    )
    base = select(DocumentInstance).where(
        DocumentInstance.workspace_uuid == workspace_uuid,
    )
    if not is_workspace_admin(roles):
        base = base.where(
            (DocumentInstance.requester_member_uuid == caller_member_uuid)
            | (DocumentInstance.subject_member_uuid == caller_member_uuid)
        )
    if filters.state is not None:
        base = base.where(DocumentInstance.state == filters.state)
    if filters.template_uuid is not None:
        base = base.where(DocumentInstance.template_uuid == filters.template_uuid)
    if filters.subject_member_uuid is not None:
        base = base.where(
            DocumentInstance.subject_member_uuid == filters.subject_member_uuid
        )

    total = int(
        (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    )
    page = await db.execute(
        base.order_by(DocumentInstance.created_at.desc())
        .limit(filters.limit)
        .offset(filters.offset)
    )
    return DocumentInstanceListOutput(
        instances=[
            DocumentInstanceOutput.model_validate(i) for i in page.scalars().all()
        ],
        total=total,
    )


def _assert_transition(
    current: DocumentInstanceState,
    new: DocumentInstanceState,
) -> None:
    if new not in _VALID_INSTANCE_TRANSITIONS[current]:
        raise _bad_request(
            f"Illegal instance transition {current.value} -> {new.value}"
        )


__all__ = [
    "ReviewWorkflowOutput",
    "approve_document_instance",
    "create_document_template",
    "create_retention_policy",
    "deprecate_document_template",
    "draft_document_instance",
    "get_document_instance",
    "get_document_template",
    "issue_document_instance",
    "list_document_instances",
    "list_document_templates",
    "list_retention_policies",
    "publish_document_template",
    "reject_document_instance",
    "submit_for_review",
    "void_document_instance",
]
