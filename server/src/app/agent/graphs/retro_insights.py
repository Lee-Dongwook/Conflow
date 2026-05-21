"""Retro insights worker subgraph for LangGraph Studio validation."""
from __future__ import annotations

import os
from typing import Any, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


class RetroInsightItem(BaseModel):
    category: str = Field(description="Keep(유지할 점), Problem(문제점), Try(시도할 점) 중 하나")
    context: str = Field(description="회고 데이터에서 도출한 구체적인 핵심 내용")
    action_item: str = Field(description="해당 문제를 해결하거나 유지하기 위해 다음 주차에 수행할 실질적 행동 지침")

class RetroInsightsOutput(BaseModel):
    insights: list[RetroInsightItem] = Field(description="분석된 회고 인사이트 목록")
    team_pulse_score: int = Field(description="AI가 평가한 이번 주차 팀 협업 점수 (1~100)")
    summary: str = Field(description="팀 회고 종합 피드백 및 격려 메시지")

class RetroInsightsState(TypedDict, total=False):
    """Internal state for retro_insights subgraph."""
    current_task: str
    chat_history: list[BaseMessage]
    team_context: str | None
    detected_insights: list[dict[str, Any]]
    team_pulse_score: int
    summary: str
    agent_mode: Literal["mock", "llm"]
    error: str | None

def _resolve_agent_mode() -> Literal["mock", "llm"]:
    raw = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()
    return "llm" if raw == "llm" else "mock"


def _mock_retro(state: RetroInsightsState) -> dict[str, object]:
    """Pure heuristic generator for Studio mock mode."""
    task = state.get("current_task", "")
    
    mock_insight = {
        "category": "Problem" if "지연" in task or "늦어" in task else "Keep",
        "context": task or "이번 주차 회고 데이터가 입력되지 않았습니다.",
        "action_item": "다음 스케줄 산정 시 버퍼 기한을 2일 이상 확보할 것",
    }
    
    return {
        "detected_insights": [mock_insight],
        "team_pulse_score": 85,
        "summary": "로컬 가짜 엔진에 의해 이번 주차 회고 분석이 완료되었습니다. 팀 소통 상태는 양호합니다.",
        "agent_mode": "mock",
        "error": None
    }

def _llm_retro(state: RetroInsightsState) -> dict[str, object]:
    """Structured OpenAI call for analyzing sprint retrospectives."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "error": "CONFLOW_AGENT_MODE=llm 설정 상태이나 OPENAI_API_KEY가 없습니다.",
            "agent_mode": "llm",
        }

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    task = state.get("current_task", "")
    team_context = state.get("team_context") or "팀 컨텍스트 없음"

    system = SystemMessage(
        content=(
            "You are a Project Management Consultant for Conflow. "
            "Analyze the retrospective inputs or text context to extract structured insights based on the KPT (Keep, Problem, Try) framework. "
            "Evaluate team collaboration health and suggest concrete action items. "
            "Respond in concise Korean."
        )
    )
    human = HumanMessage(
        content=f"회고 데이터 및 맥락: {task}\n팀 컨텍스트: {team_context}"
    )

    llm = ChatOpenAI(model=model_name, temperature=0.1)
    structured = llm.with_structured_output(RetroInsightsOutput)
    result: RetroInsightsOutput = structured.invoke([system, human])

    return {
        "detected_insights": [item.model_dump() for item in result.insights],
        "team_pulse_score": result.team_pulse_score,
        "summary": result.summary,
        "agent_mode": "llm",
        "error": None
    }

def validate_input(state: RetroInsightsState) -> dict[str, object]:
    task = (state.get("current_task") or "").strip()
    return {
        "current_task": task,
        "error": None
    }


def route_after_validate(state: RetroInsightsState) -> Literal["retro_analysis", "__end__"]:
    return "__end__" if state.get("error") else "retro_analysis"


def retro_analysis(state: RetroInsightsState) -> dict[str, object]:
    mode = _resolve_agent_mode()
    if mode == "llm":
        return _llm_retro(state)
    return _mock_retro(state)

def build_graph() -> StateGraph:
    builder = StateGraph(RetroInsightsState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("retro_analysis", retro_analysis)
    
    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges(
        "validate_input",
        route_after_validate,
        {"retro_analysis": "retro_analysis", "__end__": END},
    )
    builder.add_edge("retro_analysis", END)
    return builder


graph = build_graph().compile()
