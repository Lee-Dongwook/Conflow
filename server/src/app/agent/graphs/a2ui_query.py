"""A2UI query graph — invokes a registered Tool inside LangGraph.

Bridges LangGraph state ↔ A2UI dispatcher. The state carries an `intent`
(Tool id OR cross-domain plan key) + raw input; the graph runs the Tool
through the same `invoke_tool` pipeline that the HTTP layer uses, so
Tier + permission + audit are uniformly enforced.

Caller context (workspace_uuid, caller_member_uuid) is read from
`RunnableConfig.configurable` — the supervisor injects it at graph entry
and the Tool dispatcher uses it as `caller`. The graph itself never
trusts state fields for context, which would let an LLM spoof them.

Mode policy:
  - MOCK   → tool execution skipped; emits a structured placeholder.
  - LLM/OLLAMA/VLLM → real `invoke_tool` call against the configured DB session.

The supervisor routing wire-up (intent='a2ui' → this graph) lands as
a follow-up; for now this graph is invokable standalone via
`graph.ainvoke(state, config=RunnableConfig(configurable={...}))`.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from ...core.runtime import logger
from ..mode import is_mock


class A2UIQueryState(TypedDict, total=False):
    """State threaded through the a2ui_query graph."""

    tool_id: str
    raw_input: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None
    error_status_code: int | None
    agent_mode: Literal["mock", "llm"]


def _ctx_missing(config: RunnableConfig | None) -> str | None:
    """Return a human-readable error if required caller context is missing."""
    cfg = (config or {}).get("configurable") or {}
    for required in ("workspace_uuid", "caller_member_uuid", "db_session"):
        if not cfg.get(required):
            return f"missing config: {required}"
    return None


async def invoke_a2ui_tool_node(
    state: A2UIQueryState,
    config: RunnableConfig | None = None,
) -> dict[str, Any]:
    """Run the A2UI Tool dispatcher and write result/error into state."""
    tool_id = state.get("tool_id")
    raw_input = state.get("raw_input") or {}

    if not tool_id:
        return {
            "error": "tool_id is required",
            "error_status_code": 400,
            "agent_mode": "mock" if is_mock() else "llm",
        }

    if is_mock():
        # Deterministic placeholder — keeps tests/CI free of LLM/DB
        # dependence while exercising the routing path.
        logger.info("a2ui_query mock invoke: tool_id=%s", tool_id)
        return {
            "result": {
                "tool_id": tool_id,
                "mock": True,
                "echo_input": raw_input,
            },
            "agent_mode": "mock",
        }

    ctx_err = _ctx_missing(config)
    if ctx_err is not None:
        return {
            "error": ctx_err,
            "error_status_code": 400,
            "agent_mode": "llm",
        }

    cfg = (config or {}).get("configurable") or {}
    workspace_uuid = cfg["workspace_uuid"]
    caller_member_uuid = cfg["caller_member_uuid"]
    db = cfg["db_session"]

    # Local import: avoid the agent → core.a2ui → core.permissions →
    # core.shared cycle at module load.
    from ...core.a2ui import ToolInvocationError, invoke_tool  # noqa: PLC0415

    try:
        result = await invoke_tool(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=caller_member_uuid,
            tool_id=tool_id,
            raw_input=raw_input,
            db=db,
        )
        return {
            "result": result.model_dump(mode="json"),
            "agent_mode": "llm",
        }
    except ToolInvocationError as exc:
        return {
            "error": str(exc.detail),
            "error_status_code": exc.status_code,
            "agent_mode": "llm",
        }


def build_graph() -> StateGraph:
    """Compile the a2ui_query graph. Single node — placeholder for future
    multi-step composition (e.g. clarification → invoke → format)."""
    g = StateGraph(A2UIQueryState)
    g.add_node("invoke_a2ui_tool", invoke_a2ui_tool_node)
    g.add_edge(START, "invoke_a2ui_tool")
    g.add_edge("invoke_a2ui_tool", END)
    return g


graph = build_graph().compile()


__all__ = [
    "A2UIQueryState",
    "build_graph",
    "graph",
    "invoke_a2ui_tool_node",
]
