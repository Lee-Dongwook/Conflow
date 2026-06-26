"""A2UI HTTP routes — Tool catalog + invocation.

`GET  /workspaces/{ws}/a2ui/tools`           — Tier-filtered catalog
`POST /workspaces/{ws}/a2ui/tools/{id}/invoke` — dispatch through registry

The catalog endpoint exposes the input/output JSON schema for each Tool so
agent runtimes (LangGraph + others) can introspect without re-deriving
from Python types.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..deps import get_caller_member
from ..shared import Member, Workspace
from .dispatcher import invoke_tool
from .registry import list_tools

router = APIRouter(prefix="/workspaces/{workspace_uuid}/a2ui", tags=["a2ui"])


class ToolCatalogEntry(BaseModel):
    id: str
    domain: str
    description: str
    min_tier: str
    permission_required: str
    cross_domain: bool
    phase: int
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    tags: list[str]


class ToolCatalogOutput(BaseModel):
    tools: list[ToolCatalogEntry]


@router.get("/tools", response_model=ToolCatalogOutput)
async def list_tools_endpoint(
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),  # noqa: ARG001
    db: AsyncSession = Depends(get_async_db),
) -> ToolCatalogOutput:
    res = await db.execute(
        select(Workspace.tier).where(Workspace.uuid == workspace_uuid)
    )
    tier = res.scalar_one_or_none()
    available = list_tools(max_tier=tier) if tier is not None else []
    return ToolCatalogOutput(
        tools=[
            ToolCatalogEntry(
                id=t.id,
                domain=t.domain,
                description=t.description,
                min_tier=t.min_tier.value,
                permission_required=t.permission_required.value,
                cross_domain=t.cross_domain,
                phase=t.phase,
                input_schema=t.input_schema.model_json_schema(),
                output_schema=t.output_schema.model_json_schema(),
                tags=list(t.tags),
            )
            for t in available
        ]
    )


class ToolInvokeOutput(BaseModel):
    tool_id: str
    result: dict[str, Any]


@router.post("/tools/{tool_id}/invoke", response_model=ToolInvokeOutput)
async def invoke_tool_endpoint(
    tool_id: str,
    raw_input: dict[str, Any] = Body(default_factory=dict),
    workspace_uuid: str = Path(...),
    caller: Member = Depends(get_caller_member),
    db: AsyncSession = Depends(get_async_db),
) -> ToolInvokeOutput:
    result = await invoke_tool(
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller.uuid,
        tool_id=tool_id,
        raw_input=raw_input,
        db=db,
    )
    return ToolInvokeOutput(
        tool_id=tool_id,
        result=result.model_dump(mode="json"),
    )
