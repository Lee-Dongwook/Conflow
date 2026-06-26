"""Pydantic Input / Output schemas for Documents service functions."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .model import (
    DocumentCategory,
    DocumentInstanceState,
    ReviewWorkflowState,
    TemplateState,
)

# ---------------------------------------------------------------------------
# RetentionPolicy
# ---------------------------------------------------------------------------


class RetentionPolicyCreateInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    # None = retain indefinitely (statutory infinite, e.g. 근로계약서)
    retention_days: int | None = Field(default=None, ge=0)
    immutable: bool = False


class RetentionPolicyOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    name: str
    retention_days: int | None
    immutable: bool
    created_at: datetime
    updated_at: datetime


class RetentionPolicyListOutput(BaseModel):
    policies: list[RetentionPolicyOutput]


# ---------------------------------------------------------------------------
# DocumentTemplate
# ---------------------------------------------------------------------------


class DocumentTemplateCreateInput(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: DocumentCategory
    subtype: str = Field(min_length=1, max_length=64)
    body_md: str = Field(min_length=1)
    variables_schema: list[dict[str, Any]] = Field(default_factory=list)
    default_retention_policy_uuid: str
    requires_signature: bool = False
    version: str = Field(default="1.0.0", max_length=32)


class DocumentTemplateOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    name: str
    category: DocumentCategory
    subtype: str
    body_md: str
    variables_schema: list[dict[str, Any]]
    default_review_workflow_uuid: str | None
    default_retention_policy_uuid: str
    requires_signature: bool
    version: str
    state: TemplateState
    published_at: datetime | None
    created_by_member_uuid: str
    created_at: datetime
    updated_at: datetime


class DocumentTemplateListFilter(BaseModel):
    category: DocumentCategory | None = None
    state: TemplateState | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class DocumentTemplateListOutput(BaseModel):
    templates: list[DocumentTemplateOutput]
    total: int


# ---------------------------------------------------------------------------
# DocumentInstance
# ---------------------------------------------------------------------------


class DocumentInstanceDraftInput(BaseModel):
    template_uuid: str
    subject_member_uuid: str | None = None
    variables_snapshot: dict[str, Any] = Field(default_factory=dict)


class DocumentInstanceVoidInput(BaseModel):
    void_reason: str = Field(min_length=1)


class DocumentInstanceOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    template_uuid: str
    template_version: str
    subject_member_uuid: str | None
    requester_member_uuid: str
    variables_snapshot: dict[str, Any]
    rendered_pdf_uri: str | None
    state: DocumentInstanceState
    review_workflow_uuid: str | None
    signature_request_uuid: str | None
    retention_policy_uuid: str
    retention_expires_at: datetime | None
    issued_at: datetime | None
    void_reason: str | None
    created_at: datetime
    updated_at: datetime


class DocumentInstanceListFilter(BaseModel):
    state: DocumentInstanceState | None = None
    template_uuid: str | None = None
    subject_member_uuid: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class DocumentInstanceListOutput(BaseModel):
    instances: list[DocumentInstanceOutput]
    total: int


class ReviewWorkflowOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    workspace_uuid: str
    instance_uuid: str
    steps_count: int
    current_step_index: int
    state: ReviewWorkflowState
    created_at: datetime
    updated_at: datetime
