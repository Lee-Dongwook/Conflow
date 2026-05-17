"""
Supervisor Agent Graph — orchestrates worker agents (meeting_summary, blocker_triage, …).

LangGraph API (`langgraph dev`): no custom checkpointer; nodes return state patches.
`meeting_summary` worker invokes the real child graph (mock/llm via CONFLOW_AGENT_MODE).
"""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from src.app.agent.graphs.workers import (
    default_transcript_when_missing,
    format_meeting_summary_for_supervisor,
    invoke_meeting_summary,
)

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
    meeting_title: str
    transcript: str
    team_context: str | None
    overview: str
    bullets: list[str]
    decisions: list[str]
    actions: list[dict[str, str]]
    next_steps: list[str]


def _message_content(message: BaseMessage | dict[str, Any]) -> str:
    """Extract text from a message object or Studio JSON dict."""
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


def _chat_text(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Join human-side chat lines for transcript fallback."""
    return "\n".join(
        text
        for message in chat_history
        if (text := _message_content(message).strip())
    )


def _task_from_chat(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Infer task text when Studio omits `current_task`."""
    if not chat_history:
        return "Process the team collaboration request."
    return _message_content(chat_history[-1]) or "Process the team collaboration request."


def _transcript_from_state(state: AgentState) -> str:
    """Resolve transcript: explicit field → chat → dev sample."""
    explicit = (state.get("transcript") or "").strip()
    if explicit:
        return explicit
    return default_transcript_when_missing(_chat_text(state.get("chat_history") or []))


def _meeting_title_from_state(state: AgentState, current_task: str) -> str:
    """Resolve meeting title for the child graph."""
    title = (state.get("meeting_title") or "").strip()
    return title or current_task[:256] or "회의"


# Natural-language hints → route to meeting_summary (no LLM; keyword router).
_MEETING_SUMMARY_HINTS: tuple[str, ...] = (
    "meeting",
    "summary",
    "minutes",
    "minute",
    "standup",
    "stand-up",
    "huddle",
    "회의",
    "회의록",
    "미팅",
    "스탠드업",
    "전사",
    "허들",
    "요약해",
    "정리해",
)


def _wants_meeting_summary(intent_text: str) -> bool:
    """True when user instruction looks like meeting minutes / 회의록."""
    lowered = intent_text.lower()
    return any(hint in lowered for hint in _MEETING_SUMMARY_HINTS)


def _intent_text(state: AgentState, current_task: str) -> str:
    """Combine task line and chat for routing."""
    chat = _chat_text(state.get("chat_history") or [])
    if chat and chat not in current_task:
        return f"{current_task}\n{chat}"
    return current_task


def _pick_route(current_task: str, agent_output: str, *, intent_text: str) -> RouteKey:
    """Rule-based routing (supervisor brain; worker outputs drive completion)."""
    output_lower = agent_output.lower()

    if "summary complete" in output_lower:
        return "FINISH"

    if "mock output" in output_lower:
        return "FINISH"

    if "meeting_summary error" in output_lower:
        return "FINISH"

    if _wants_meeting_summary(intent_text):
        return "meeting_summary"

    task_lower = intent_text.lower()

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
    intent = _intent_text(state, current_task)
    next_agent = _pick_route(current_task, agent_output, intent_text=intent)

    print(
        f"--- Supervisor: task={current_task!r} output={agent_output!r} -> {next_agent} ---",
    )

    patch: dict[str, Any] = {
        "current_task": current_task,
        "agent_output": agent_output,
        "chat_history": chat_history,
        "next_agent": next_agent,
    }
    for key in ("overview", "bullets", "decisions", "actions", "next_steps"):
        if key in state:
            patch[key] = state[key]
    return patch


def route_after_decide(state: AgentState) -> RouteKey:
    """Conditional edge: read `next_agent` set by supervisor_decide."""
    return state.get("next_agent") or "FINISH"


def _invoke_meeting_summary_worker(
    state: AgentState,
    current_task: str,
) -> dict[str, Any]:
    """Call meeting_summary graph and map result into supervisor state."""
    meeting_title = _meeting_title_from_state(state, current_task)
    transcript = _transcript_from_state(state)
    team_context = state.get("team_context")

    print(
        f"--- Supervisor: invoking meeting_summary "
        f"title={meeting_title!r} transcript_len={len(transcript)} ---",
    )

    result = invoke_meeting_summary(
        meeting_title=meeting_title,
        transcript=transcript,
        team_context=team_context,
    )
    agent_output = format_meeting_summary_for_supervisor(result)
    prior = list(state.get("chat_history") or [])
    new_history = [*prior, AIMessage(content=agent_output)]

    patch: dict[str, Any] = {
        "current_task": current_task,
        "agent_output": agent_output,
        "chat_history": new_history,
        "meeting_title": meeting_title,
        "transcript": transcript,
    }
    if team_context:
        patch["team_context"] = team_context

    for key in ("overview", "bullets", "decisions", "actions", "next_steps", "error"):
        if key in result and result[key] is not None:
            patch[key] = result[key]

    return patch


def _invoke_placeholder_worker(next_agent: RouteKey, current_task: str) -> str:
    """Stub workers not yet implemented as graphs."""
    completion_tag = {
        "blocker_triage": "blocker found",
        "retro_insights": "insights generated",
    }.get(next_agent, "step complete")
    return f"Mock output from {next_agent} for '{current_task}'. ({completion_tag})"


def call_worker_agent_node(state: AgentState) -> dict[str, Any]:
    """Invoke the selected worker graph or placeholder."""
    next_agent = state.get("next_agent") or "meeting_summary"
    current_task = state.get("current_task") or _task_from_chat(
        state.get("chat_history") or [],
    )

    if next_agent == "meeting_summary":
        return _invoke_meeting_summary_worker(state, current_task)

    print(f"--- Supervisor: placeholder worker={next_agent} ---")
    worker_text = _invoke_placeholder_worker(next_agent, current_task)
    prior = list(state.get("chat_history") or [])
    return {
        "current_task": current_task,
        "agent_output": worker_text,
        "chat_history": [*prior, AIMessage(content=worker_text)],
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
