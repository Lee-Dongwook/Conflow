"""Meeting summary graph — Phase 2 Conflow agent (transcript → A2UI-shaped output)."""

from __future__ import annotations

import os
import re
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from src.app.agent.graphs.schemas import MeetingSummaryOutput

MAX_TRANSCRIPT_CHARS = 48_000


class MeetingSummaryState(TypedDict, total=False):
    """State threaded through the meeting_summary graph."""

    meeting_title: str
    transcript: str
    team_context: str | None
    overview: str
    bullets: list[str]
    decisions: list[str]
    actions: list[dict[str, str]]
    next_steps: list[str]
    agent_mode: Literal["mock", "llm"]
    error: str | None


def _resolve_agent_mode() -> Literal["mock", "llm"]:
    """Resolve runtime mode from environment."""
    raw = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()
    return "llm" if raw == "llm" else "mock"


def _sentences(text: str) -> list[str]:
    """Split transcript into coarse sentences."""
    parts = re.split(r"[.!?。\n]+", text)
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def _mock_summarize(state: MeetingSummaryState) -> dict[str, object]:
    """Heuristic summary for local dev without an LLM API key."""
    title = state.get("meeting_title", "회의")
    sentences = _sentences(state.get("transcript", ""))
    overview_source = sentences[0] if sentences else title
    overview = (
        overview_source
        if len(overview_source) <= 200
        else f"{overview_source[:197]}..."
    )

    decision_keywords = ("하기로", "로 한다", "필수", "유지", "제한", "기준")
    action_keywords = ("보강", "남기", "터치", "제안", "담당", "코멘트")
    next_keywords = ("다음", "수요일", "금요일", "허들", "까지")

    decisions = [s for s in sentences if any(k in s for k in decision_keywords)][:5]
    bullets = [s for s in sentences if s not in decisions][:6]
    next_steps = [s for s in sentences if any(k in s for k in next_keywords)][:5]

    actions: list[dict[str, str]] = []
    for sentence in sentences:
        if not any(k in sentence for k in action_keywords):
            continue
        owner = "미정"
        owner_match = re.search(r"([가-힣A-Za-z○]+)가\s", sentence)
        if owner_match:
            owner = owner_match.group(1)
        actions.append({"task": sentence, "owner": owner})
        if len(actions) >= 5:
            break

    if not bullets and sentences:
        bullets = sentences[:4]

    return {
        "overview": overview,
        "bullets": bullets,
        "decisions": decisions,
        "actions": actions,
        "next_steps": next_steps,
        "agent_mode": "mock",
    }


def _llm_summarize(state: MeetingSummaryState) -> dict[str, object]:
    """Structured LLM extraction when OPENAI_API_KEY is set."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "error": "CONFLOW_AGENT_MODE=llm but OPENAI_API_KEY is missing",
            "agent_mode": "llm",
        }

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    team_context = state.get("team_context") or "팀 컨텍스트 없음"
    title = state.get("meeting_title", "회의")
    transcript = state.get("transcript", "")

    system = SystemMessage(
        content=(
            "You extract structured meeting notes for a Korean university/study team "
            "collaboration tool (Conflow). "
            "Return concise Korean text. "
            "Do not invent facts not present in the transcript."
        ),
    )
    human = HumanMessage(
        content=(
            f"회의 제목: {title}\n"
            f"팀 맥락: {team_context}\n\n"
            f"전사:\n{transcript}"
        ),
    )

    llm = ChatOpenAI(model=model_name, temperature=0.2)
    structured = llm.with_structured_output(MeetingSummaryOutput)
    result: MeetingSummaryOutput = structured.invoke([system, human])

    return {
        "overview": result.overview,
        "bullets": result.bullets,
        "decisions": result.decisions,
        "actions": [item.model_dump() for item in result.actions],
        "next_steps": result.next_steps,
        "agent_mode": "llm",
    }


def validate_input(state: MeetingSummaryState) -> dict[str, object]:
    """Validate required fields and transcript length."""
    title = (state.get("meeting_title") or "").strip()
    transcript = (state.get("transcript") or "").strip()

    if not title:
        return {"error": "meeting_title is required"}
    if not transcript:
        return {"error": "transcript is required"}
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        return {
            "error": f"transcript exceeds {MAX_TRANSCRIPT_CHARS} characters",
        }

    return {
        "meeting_title": title,
        "transcript": transcript,
        "team_context": (state.get("team_context") or "").strip() or None,
        "error": None,
    }


def route_after_validate(
    state: MeetingSummaryState,
) -> Literal["summarize", "__end__"]:
    """Skip summarize when validation failed."""
    return "__end__" if state.get("error") else "summarize"


def summarize(state: MeetingSummaryState) -> dict[str, object]:
    """Produce structured summary via mock or LLM."""
    mode = _resolve_agent_mode()
    if mode == "llm":
        return _llm_summarize(state)
    return _mock_summarize(state)


def build_graph() -> StateGraph:
    """Build the meeting summary StateGraph (uncompiled)."""
    builder = StateGraph(MeetingSummaryState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("summarize", summarize)
    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges(
        "validate_input",
        route_after_validate,
        {"summarize": "summarize", "__end__": END},
    )
    builder.add_edge("summarize", END)
    return builder


graph = build_graph().compile()
