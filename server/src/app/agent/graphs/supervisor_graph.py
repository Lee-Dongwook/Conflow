"""
Supervisor Agent Graph — orchestrates worker agents (meeting_summary, blocker_triage, …).

LangGraph API (`langgraph dev`): no custom checkpointer; nodes must return state patches,
not routing strings. Routing uses a separate function reading `next_agent` from state.
"""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

RouteKey = Literal[
    "meeting_summary",
    "blocker_triage",
    "retro_insights",
    "FINISH",
    "REVISE",
    "DELEGATE",
]


class AgentState(TypedDict, total=False):
    """Supervisor graph state (Studio / API input)."""

    current_task: str
    agent_output: str
    chat_history: list[BaseMessage]
    next_agent: RouteKey


def _message_content(message: BaseMessage | dict[str, Any]) -> str:
    """Extract text from a message object or Studio JSON dict."""
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


def _task_from_chat(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Infer task text when Studio omits `current_task`."""
    if not chat_history:
        return "Process the team collaboration request."
    return _message_content(chat_history[-1]) or "Process the team collaboration request."


def _pick_route(current_task: str, agent_output: str) -> RouteKey:
    """Rule-based routing (mock supervisor brain)."""
    task_lower = current_task.lower()
    output_lower = agent_output.lower()

    if "mock output" in output_lower:
        return "FINISH"

    if "meeting" in task_lower or "summary" in task_lower or "standup" in task_lower:
        if "summary complete" not in output_lower:
            return "meeting_summary"

    if "blocker" in task_lower and "blocker found" not in output_lower:
        return "blocker_triage"

    if "retro" in task_lower and "insights generated" not in output_lower:
        return "retro_insights"

    return "FINISH"


def supervisor_decide(state: AgentState) -> dict[str, Any]:
    """Update state with routing decision (`next_agent`)."""
    current_task = (state.get("current_task") or "").strip() or _task_from_chat(
        state.get("chat_history") or [],
    )
    agent_output = state.get("agent_output") or ""
    chat_history = list(state.get("chat_history") or [])
    next_agent = _pick_route(current_task, agent_output)

    print(
        f"--- Supervisor: task={current_task!r} output={agent_output!r} -> {next_agent} ---",
    )

    return {
        "current_task": current_task,
        "agent_output": agent_output,
        "chat_history": chat_history,
        "next_agent": next_agent,
    }


def route_after_decide(state: AgentState) -> RouteKey:
    """Conditional edge: read `next_agent` set by supervisor_decide."""
    return state.get("next_agent") or "FINISH"


def call_worker_agent_node(state: AgentState) -> dict[str, Any]:
    """Invoke a worker agent (mock) and append to chat history."""
    next_agent = state.get("next_agent") or "meeting_summary"
    current_task = state.get("current_task") or _task_from_chat(
        state.get("chat_history") or [],
    )

    print(f"--- Supervisor: worker={next_agent} task={current_task!r} ---")

    completion_tag = {
        "meeting_summary": "summary complete",
        "blocker_triage": "blocker found",
        "retro_insights": "insights generated",
    }.get(next_agent, "step complete")
    mock_output = (
        f"Mock output from {next_agent} for '{current_task}'. ({completion_tag})"
    )
    prior = list(state.get("chat_history") or [])
    new_history = [*prior, HumanMessage(content=mock_output)]

    return {
        "current_task": current_task,
        "agent_output": mock_output,
        "chat_history": new_history,
    }


workflow = StateGraph(AgentState)
workflow.add_node("decide_next_step", supervisor_decide)
workflow.add_node("call_worker_agent", call_worker_agent_node)
workflow.set_entry_point("decide_next_step")
workflow.add_conditional_edges(
    "decide_next_step",
    route_after_decide,
    {
        "meeting_summary": "call_worker_agent",
        "blocker_triage": "call_worker_agent",
        "retro_insights": "call_worker_agent",
        "DELEGATE": "call_worker_agent",
        "FINISH": END,
        "REVISE": "decide_next_step",
    },
)
workflow.add_edge("call_worker_agent", "decide_next_step")

supervisor_agent_graph = workflow.compile()


if __name__ == "__main__":
    initial: AgentState = {
        "current_task": "Generate a meeting summary for the last standup.",
        "agent_output": "",
        "chat_history": [HumanMessage(content="Please summarize the standup meeting.")],
    }
    for chunk in supervisor_agent_graph.stream(initial):
        print(chunk)
        print("---")
