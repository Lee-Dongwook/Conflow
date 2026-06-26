"""A2UI ↔ LangChain Tool bridge.

Wraps registered A2UI ToolSpecs as LangChain `BaseTool` instances so they
can be bound to an LLM via `llm.bind_tools(...)` inside LangGraph nodes.

The supervisor / per-domain agents stay thin: pick the Tool subset they
need (e.g. only `pm.*` for the blocker_triage worker), and let the
A2UI dispatcher do gating + audit. The wrapper enforces that the caller
context (workspace + member + db session) is captured at bind time —
NEVER trusted from LLM input.

Real LangGraph supervisor wiring lands in a later step alongside the
mock/llm switching policy in `agent/graphs/supervisor_graph.py`. This
module is the contract those nodes will import.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from langchain_core.tools import StructuredTool
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.a2ui import ToolSpec, get_tool, invoke_tool, list_tools


def _tool_safe_name(tool_id: str) -> str:
    """LangChain function-tool names must match `^[a-zA-Z0-9_-]+$`.
    `pm.search_issues` → `pm_search_issues`.
    """
    return tool_id.replace(".", "_")


def make_langchain_tool(
    spec: ToolSpec,
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    db: AsyncSession,
) -> StructuredTool:
    """Bind one ToolSpec as a LangChain `StructuredTool`.

    The caller context (workspace + member + db) is captured by closure
    so the LLM cannot spoof a different tenant via the function arguments.
    """

    async def _coroutine(**kwargs: Any) -> dict[str, Any]:
        result = await invoke_tool(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=caller_member_uuid,
            tool_id=spec.id,
            raw_input=kwargs,
            db=db,
        )
        return result.model_dump(mode="json")

    return StructuredTool.from_function(
        coroutine=_coroutine,
        name=_tool_safe_name(spec.id),
        description=spec.description,
        args_schema=spec.input_schema,
    )


def bind_tools_for_caller(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    db: AsyncSession,
    tool_ids: Iterable[str] | None = None,
    domain: str | None = None,
) -> list[StructuredTool]:
    """Bind a subset of registered Tools for a single caller context.

    Without filters: all registered Tools. With `tool_ids`: only those.
    With `domain`: all Tools in that domain (e.g. `"pm"` for a PM agent).
    """
    if tool_ids is not None:
        specs = [get_tool(tid) for tid in tool_ids]
    else:
        specs = list_tools(domain=domain)
    return [
        make_langchain_tool(
            s,
            workspace_uuid=workspace_uuid,
            caller_member_uuid=caller_member_uuid,
            db=db,
        )
        for s in specs
    ]
