"""Documents domain Tools — register at import."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....documents.model import DocumentInstanceState
from ....documents.schemas import (
    DocumentInstanceListFilter,
    DocumentInstanceListOutput,
)
from ....documents.service import list_document_instances
from ...shared import WorkspaceTier
from ..registry import PermissionLevel, ToolSpec, register_tool


class DocsListPendingReviewInput(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


async def _docs_list_pending_review(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: DocsListPendingReviewInput,
    db: AsyncSession,
) -> DocumentInstanceListOutput:
    return await list_document_instances(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        filters=DocumentInstanceListFilter(
            state=DocumentInstanceState.PENDING_REVIEW,
            limit=payload.limit,
            offset=payload.offset,
        ),
        db=db,
    )


register_tool(
    ToolSpec(
        id="documents.list_pending_review",
        domain="documents",
        description=(
            "List document instances currently in PENDING_REVIEW. Scope is "
            "Admin = all, non-Admin = own (requester or subject) only."
        ),
        handler=_docs_list_pending_review,
        input_schema=DocsListPendingReviewInput,
        output_schema=DocumentInstanceListOutput,
        min_tier=WorkspaceTier.BUSINESS,
        permission_required=PermissionLevel.MEMBER,
        phase=2,
    )
)
