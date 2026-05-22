"""
Supervisor Agent Graph — orchestrates worker agents (meeting_summary, blocker_triage, …).

Routing runs through the compiled ``user_query`` subgraph (``analyze_user_query``) so
LangGraph Studio shows intent classification inside the parent run. ``meeting_summary``
is a second subgraph for the minutes worker.
"""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from src.app.agent.graphs.base_agent_state import AgentState
from src.app.agent.graphs.blocker_triage import graph as blocker_triage_graph
from src.app.agent.graphs.file_analysis import graph as file_analysis_graph
from src.app.agent.graphs.meeting_summary import graph as meeting_summary_graph
from src.app.agent.graphs.retro_insights import graph as retro_insights_graph
from src.app.agent.graphs.slack_notifier import slack_mcp_notifier
from src.app.agent.graphs.user_query import RouteKey, task_from_chat
from src.app.agent.graphs.user_query import graph as user_query_graph
from src.app.agent.graphs.workers import (
    default_transcript_when_missing,
    format_meeting_summary_for_supervisor,
)
from src.app.core.shared import logger

FINISH: Literal["FINISH"] = "FINISH"
RETRY: Literal["RETRY"] = "RETRY"
DEFAULT_MEETING_TITLE = "회의"
MAX_MEETING_TITLE_CHARS = 256
MAX_WINDOW_SIZE = 6

PLACEHOLDER_COMPLETION_TAGS: dict[RouteKey, str] = {
    "blocker_triage": "blocker found",
    "retro_insights": "insights generated",
    "file_analysis": "file analysis complete",
    "search": "search complete",
}

def compress_context_node(state: AgentState) -> dict[str, Any]:
    """Compress the context window to the last MAX_WINDOW_SIZE messages."""
    messages = state.get("chat_history") or []
    current_summary = state.get("summary") or ""

    if len(messages) <= MAX_WINDOW_SIZE:
        return {}

    messages_to_summarize = messages[:-4]

    summary_prompt = (
        "You are an expert context compressor for Conflow Project Management System.\n"
        "Analyze the following conversation segment and update the existing summary.\n"
        "Focus on core task updates, project blockers, and engineering decisions.\n\n"
        f"■ Current Summary Base:\n{current_summary}\n\n"
        "■ New Conversation Segment to integrate:"
    )

    formatted_chat = ""
    for msg in messages_to_summarize:
        role = "User" if msg.type == "human" else "Agent"
        formatted_chat += f"{role}: {msg.content}\n"

    summary_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    response = summary_llm.invoke(
        [
            SystemMessage(content=summary_prompt),
            HumanMessage(content=formatted_chat),
        ]
    )

    updated_summary = str(response.content).strip()

    purge_signals = [RemoveMessage(id=msg.id) for msg in messages_to_summarize]

    return {"summary": updated_summary, "chat_history": purge_signals}


def _chat_text(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Join human-side chat lines for transcript fallback."""
    from src.app.agent.graphs.user_query import chat_text

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
    return title or current_task[:MAX_MEETING_TITLE_CHARS] or DEFAULT_MEETING_TITLE


def _current_task_from_state(state: AgentState) -> str:
    """Return explicit task text, falling back to the latest chat message."""
    return (state.get("current_task") or "").strip() or task_from_chat(
        state.get("chat_history") or [],
    )


def prepare_user_query_input(state: AgentState) -> dict[str, Any]:
    """Normalize supervisor state before the user_query subgraph."""
    current_task = _current_task_from_state(state)
    logger.info("supervisor prepare user_query", extra={"task": current_task})
    return {
        "current_task": current_task,
        "agent_output": state.get("agent_output") or "",
        "chat_history": list(state.get("chat_history") or []),
        "summary": state.get("summary") or "",
    }


def route_after_user_query(state: AgentState) -> RouteKey:
    """Conditional edge: read ``next_agent`` set by the user_query subgraph."""
    return state.get("next_agent") or FINISH


def prepare_meeting_summary_input(state: AgentState) -> dict[str, Any]:
    """Map supervisor state → meeting_summary subgraph input (shared keys)."""
    current_task = _current_task_from_state(state)
    meeting_title = _meeting_title_from_state(state, current_task)
    transcript = _transcript_from_state(state)

    logger.info(
        "supervisor prepare meeting_summary title=%r transcript_len=%d",
        meeting_title,
        len(transcript),
    )

    patch: dict[str, Any] = {
        "current_task": current_task,
        "meeting_title": meeting_title,
        "transcript": transcript,
        "summary": state.get("summary") or "",
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

    logger.info("supervisor finalize meeting_summary")

    return {
        "current_task": current_task,
        "next_agent": FINISH,
        "agent_output": agent_output,
        "chat_history": [*prior, AIMessage(content=agent_output)],
        "user_feedback": None,
    }


def commit_meeting_summary(state: AgentState) -> dict[str, Any]:
    """Commit or retry a generated meeting summary after HITL review."""
    user_feedback = state.get("user_feedback")
    logger.info("User feedback received: %s", user_feedback)

    if user_feedback == "approve":
        logger.info("User feedback approved, committing meeting summary")
        return {
            "user_feedback": "approve",
            "error": None,
        }

    if user_feedback == "reject":
        logger.info("User feedback rejected, retrying")
        return {
            "user_feedback": "reject",
            "current_task": state.get("current_task") or "",
        }

    return {"user_feedback": "reject", "error": "Invalid user feedback"}


def route_after_review(state: AgentState) -> Literal["FINISH", "RETRY"]:
    """Route from the HITL review node."""
    feedback = state.get("user_feedback")
    if feedback == "approve":
        return FINISH
    return RETRY


def _invoke_placeholder_worker(next_agent: RouteKey, current_task: str) -> str:
    """Stub workers not yet implemented as graphs."""
    completion_tag = PLACEHOLDER_COMPLETION_TAGS.get(next_agent, "step complete")
    return f"Mock output from {next_agent} for '{current_task}'. ({completion_tag})"


def call_placeholder_worker(state: AgentState) -> dict[str, Any]:
    """Placeholder for blocker_triage / retro_insights / file / search."""
    next_agent = state.get("next_agent") or "blocker_triage"
    current_task = _current_task_from_state(state)

    logger.info("supervisor placeholder worker: %s", next_agent)
    worker_text = _invoke_placeholder_worker(next_agent, current_task)
    prior = list(state.get("chat_history") or [])

    return {
        "current_task": current_task,
        "agent_output": worker_text,
        "chat_history": [*prior, AIMessage(content=worker_text)],
    }


def build_graph() -> StateGraph:
    """Build the supervisor graph with routing and worker subgraphs."""
    workflow = StateGraph(AgentState)
    workflow.add_node("compress_context", compress_context_node)
    workflow.add_node("prepare_user_query", prepare_user_query_input)
    workflow.add_node("user_query", user_query_graph)
    workflow.add_node("prepare_meeting_summary", prepare_meeting_summary_input)
    workflow.add_node("meeting_summary", meeting_summary_graph)
    workflow.add_node("finalize_meeting_summary", finalize_meeting_summary)
    workflow.add_node("commit_meeting_summary", commit_meeting_summary)
    workflow.add_node("call_placeholder_worker", call_placeholder_worker)
    workflow.add_node("blocker_triage_graph", blocker_triage_graph)
    workflow.add_node("retro_insights_graph", retro_insights_graph)
    workflow.add_node("file_analysis_graph", file_analysis_graph)
    workflow.add_node("slack_notifier", slack_mcp_notifier)

    workflow.set_entry_point("compress_context")
    workflow.add_edge("compress_context", "prepare_user_query")
    workflow.add_edge("prepare_user_query", "user_query")
    workflow.add_conditional_edges(
        "user_query",
        route_after_user_query,
        {
            "meeting_summary": "prepare_meeting_summary",
            "blocker_triage": "blocker_triage_graph",
            "retro_insights": "retro_insights_graph",
            "file_analysis": "file_analysis_graph",
            "search": "call_placeholder_worker",
            FINISH: "slack_notifier",
        },
    )
    workflow.add_edge("prepare_meeting_summary", "meeting_summary")
    workflow.add_edge("meeting_summary", "finalize_meeting_summary")
    workflow.add_edge("finalize_meeting_summary", "commit_meeting_summary")

    workflow.add_conditional_edges(
        "commit_meeting_summary",
        route_after_review,
        {
            FINISH: "slack_notifier",
            RETRY: "compress_context",
        },
    )
    workflow.add_edge("slack_notifier", END)
    workflow.add_edge("call_placeholder_worker", "compress_context")
    return workflow


supervisor_agent_graph = build_graph().compile(
    interrupt_before=["commit_meeting_summary"],
)


if __name__ == "__main__":
    initial: AgentState = {
        "current_task": "Generate a meeting summary for the last standup.",
        "agent_output": "",
        "chat_history": [HumanMessage(content="Please summarize the standup meeting.")],
        "summary": "",
    }
    for chunk in supervisor_agent_graph.stream(initial):
        print(chunk)
        print("---")
