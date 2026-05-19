"""
Supervisor Agent Graph — orchestrates worker agents (meeting_summary, blocker_triage, …).

`meeting_summary` is attached as a **compiled subgraph node** so LangGraph Studio shows
validate_input → summarize inside the parent run. Other workers remain placeholders.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from src.app.agent.graphs.meeting_summary import graph as meeting_summary_graph
from src.app.agent.graphs.user_query import (
    RouteKey,
    build_intent_text,
    chat_text,
    pick_route,
    task_from_chat,
)
from src.app.agent.graphs.workers import (
    default_transcript_when_missing,
    format_meeting_summary_for_supervisor,
)
from src.app.core import logger
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """Supervisor state; includes keys shared with meeting_summary subgraph."""

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
    agent_mode: str | None
    error: str | None
    intent_text: str
    detected_urls: list[str]
    route_reason: str


def _chat_text(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Join human-side chat lines for transcript fallback."""
    return chat_text(chat_history)


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


def supervisor_decide(state: AgentState) -> dict[str, Any]:
    """Update state with routing decision (`next_agent`)."""
    current_task = (state.get("current_task") or "").strip() or task_from_chat(
        state.get("chat_history") or [],
    )
    agent_output = state.get("agent_output") or ""
    chat_history = list(state.get("chat_history") or [])
    intent = build_intent_text(current_task=current_task, chat_history=chat_history)
    next_agent, route_reason, urls = pick_route(
        current_task=current_task,
        agent_output=agent_output,
        chat_history=chat_history,
        intent_text=intent,
    )

    logger.info(
        "supervisor route: %s — %s",
        next_agent,
        route_reason,
        extra={"task": current_task},
    )

    patch: dict[str, Any] = {
        "current_task": current_task,
        "agent_output": agent_output,
        "chat_history": chat_history,
        "next_agent": next_agent,
        "intent_text": intent,
        "detected_urls": urls,
        "route_reason": route_reason,
    }
    for key in (
        "overview",
        "bullets",
        "decisions",
        "actions",
        "next_steps",
        "meeting_title",
        "transcript",
        "team_context",
        "agent_mode",
        "error",
    ):
        if key in state:
            patch[key] = state[key]
    return patch


def route_after_decide(state: AgentState) -> RouteKey:
    """Conditional edge: read `next_agent` set by supervisor_decide."""
    return state.get("next_agent") or "FINISH"


def prepare_meeting_summary_input(state: AgentState) -> dict[str, Any]:
    """Map supervisor state → meeting_summary subgraph input (shared keys)."""
    current_task = state.get("current_task") or task_from_chat(
        state.get("chat_history") or [],
    )
    meeting_title = _meeting_title_from_state(state, current_task)
    transcript = _transcript_from_state(state)

    print(
        f"--- Supervisor: prepare subgraph meeting_summary "
        f"title={meeting_title!r} transcript_len={len(transcript)} ---",
    )

    patch: dict[str, Any] = {
        "current_task": current_task,
        "meeting_title": meeting_title,
        "transcript": transcript,
        "error": None,
    }
    team_context = state.get("team_context")
    if team_context:
        patch["team_context"] = team_context
    return patch


def finalize_meeting_summary(state: AgentState) -> dict[str, Any]:
    """Format subgraph output for supervisor (agent_output + chat)."""
    summary_payload: dict[str, Any] = {
        "overview": state.get("overview"),
        "bullets": state.get("bullets"),
        "decisions": state.get("decisions"),
        "actions": state.get("actions"),
        "next_steps": state.get("next_steps"),
        "error": state.get("error"),
    }
    agent_output = format_meeting_summary_for_supervisor(summary_payload)
    prior = list(state.get("chat_history") or [])
    current_task = state.get("current_task") or ""

    print("--- Supervisor: finalize meeting_summary → agent_output ---")

    return {
        "current_task": current_task,
        "agent_output": agent_output,
        "chat_history": [*prior, AIMessage(content=agent_output)],
    }


def _invoke_placeholder_worker(next_agent: RouteKey, current_task: str) -> str:
    """Stub workers not yet implemented as graphs."""
    completion_tag = {
        "blocker_triage": "blocker found",
        "retro_insights": "insights generated",
        "file_analysis": "file analysis complete",
        "search": "search complete",
    }.get(next_agent, "step complete")
    return f"Mock output from {next_agent} for '{current_task}'. ({completion_tag})"


def call_placeholder_worker(state: AgentState) -> dict[str, Any]:
    """Placeholder for blocker_triage / retro_insights (not subgraphs yet)."""
    next_agent = state.get("next_agent") or "blocker_triage"
    current_task = state.get("current_task") or task_from_chat(
        state.get("chat_history") or [],
    )

    logger.info("supervisor placeholder worker: %s", next_agent)
    worker_text = _invoke_placeholder_worker(next_agent, current_task)
    prior = list(state.get("chat_history") or [])

    return {
        "current_task": current_task,
        "agent_output": worker_text,
        "chat_history": [*prior, AIMessage(content=worker_text)],
    }


workflow = StateGraph(AgentState)
workflow.add_node("decide_next_step", supervisor_decide)
workflow.add_node("prepare_meeting_summary", prepare_meeting_summary_input)
workflow.add_node("meeting_summary", meeting_summary_graph)
workflow.add_node("finalize_meeting_summary", finalize_meeting_summary)
workflow.add_node("call_placeholder_worker", call_placeholder_worker)

workflow.set_entry_point("decide_next_step")
workflow.add_conditional_edges(
    "decide_next_step",
    route_after_decide,
    {
        "meeting_summary": "prepare_meeting_summary",
        "blocker_triage": "call_placeholder_worker",
        "retro_insights": "call_placeholder_worker",
        "file_analysis": "call_placeholder_worker",
        "search": "call_placeholder_worker",
        "FINISH": END,
    },
)
workflow.add_edge("prepare_meeting_summary", "meeting_summary")
workflow.add_edge("meeting_summary", "finalize_meeting_summary")
workflow.add_edge("finalize_meeting_summary", "decide_next_step")
workflow.add_edge("call_placeholder_worker", "decide_next_step")

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
