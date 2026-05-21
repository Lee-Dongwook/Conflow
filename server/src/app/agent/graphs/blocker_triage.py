"""Blocker triage graph — Phase 2 Conflow agent (chat/query → Blocker entities)."""

from __future__ import annotations

import os
from typing import Any, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


class BlockerItem(BaseModel):
    context: str = Field(..., description="The context of the blocker")
    category: Literal["TECHNICAL", "RESOURCE", "COMMUNICATION", "EXTERNAL"] = Field(..., description="The category of the blocker")
    severity: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="The severity of the blocker")
    reason: str = Field(..., description="The reason for the blocker")

class BlockerTriageOutput(BaseModel):
    blockers: list[BlockerItem] = Field(..., description="The list of blockers")
    summary: str = Field(..., description="The summary of the blocker triage")

class BlockerTriageState(TypedDict, total=False):
    """State threaded through the blocker_triage graph."""

    current_task: str
    chat_history: list[BaseMessage]
    team_context: str | None

    detected_blockers: list[dict[str, Any]]
    summary: str
    agent_mode: Literal["mock", "llm"]
    error: str | None


def _resolve_agent_mode() -> Literal["mock", "llm"]:
    """Resolve runtime mode from environment."""
    raw = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()
    return "llm" if raw == "llm" else "mock"

def _mock_triage(state: BlockerTriageState) -> dict[str, object]:
    """Heuristic blocker triage for local dev without an LLM API key."""

    current_task = state.get("current_task", "")

    blockers = []
    reason = "자료 부족"
    severity = "MEDIUM"

    if "API" in current_task or "벡앤드" in current_task:
        reason = "의존성 컴포넌트 미완성 (벡앤드 API 미개방)"
        severity = "HIGH"
    elif "사정" in current_task or "아파서" in current_task:
        reason = "사정이 있어 처리 불가"
        severity = "HIGH"
    
    blockers.append({
        "context" : current_task or "테스트 병목 상황 메시지",
        "category": "TECHNICAL" if "API" in current_task else "RESOURCE",
        "severity": severity,
        "reason": reason,
        "resolved": False,
    })

    return {
        "detected_blockers": blockers,
        "summary": "병목 상황 감지",
        "agent_mode": _resolve_agent_mode()
    }


def _llm_triage(state: BlockerTriageState) -> dict[str, object]:
    """Structured LLM extraction for blocking issues."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "error": "CONFLOW_AGENT_MODE=llm but OPENAI_API_KEY is missing",
            "agent_mode": "llm",
        }
    
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    current_task = state.get("current_task", "")
    team_context = state.get("team_context") or "팀 컨텍스트 없음"

    system = SystemMessage(
        content=(
            "You are an elite Project Management AI Agent for Conflow, a team collaboration tool. "
            "Analyze the given user query or chat log to identify any blockers, bottlenecks, "
            "or issues hindering project progress. "
            "Classify each blocker into categories: 'TECHNICAL', 'RESOURCE', 'COMMUNICATION', or 'EXTERNAL'."  # noqa: E501
            "Determine severity as 'LOW', 'MEDIUM', or 'HIGH'. "
            "Return concise Korean outputs. Do not invent facts."
        ),
    )

    human = HumanMessage(
        content=(
            f"분석 대상 컨텍스트: {current_task}\n"
            f"팀 맥락: {team_context}\n"
        ),
    )

    llm = ChatOpenAI(model=model_name, temperature=0.1)
    structured = llm.with_structured_output(BlockerTriageOutput)
    result: BlockerTriageOutput = structured.invoke([system, human])

    return {
        "detected_blockers": [item.model_dump() for item in result.blockers],
        "summary": result.summary,
        "agent_mode": "llm",
    }

def validate_input(state: BlockerTriageState) -> dict[str, object]:
    """Validate input text availability."""
    current_task = (state.get("current_task") or "").strip()
    if not current_task and not state.get("chat_history"):
        return {"error": "Either current_task or chat_history is required"}
    return {"error": None}

def route_after_validate(state: BlockerTriageState) -> Literal["triage", "__end__"]:
    return "__end__" if state.get("error") else "triage"


def triage(state: BlockerTriageState) -> dict[str, object]:
    """Execute triage via mock or LLM."""
    mode = _resolve_agent_mode()
    if mode == "llm":
        return _llm_triage(state)
    return _mock_triage(state)


def build_graph() -> StateGraph:
    builder = StateGraph(BlockerTriageState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("triage", triage)
    
    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges(
        "validate_input",
        route_after_validate,
        {"triage": "triage", "__end__": END},
    )
    builder.add_edge("triage", END)
    return builder

graph = build_graph().compile()

