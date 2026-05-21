"""File analysis worker subgraph matching Conflow Pydantic state specs."""

from __future__ import annotations

import os
from typing import Literal

from langgraph.graph import END, START, StateGraph
from src.app.agent.graphs.file.model import (
    FileSubgraphOutputState,
    FileSubgraphState,
)


def _resolve_agent_mode() -> Literal["mock", "llm"]:
    raw = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()
    return "llm" if raw == "llm" else "mock"


def _mock_file_analysis(state: FileSubgraphState) -> dict[str, object]:
    """Pure heuristic analysis to feed the file_results_reducer in Studio mock mode."""
    info_list = state.file_info_list or []
    question = state.user_question or "질문 없음"
    task = state.file_task or "extract"
    
    output_results = []
    
    if not info_list:
        # 파일 리스트가 비어있을 때 가짜 파일 엔티티 생성
        output_results.append(
            FileSubgraphOutputState(
                uuid="mock-uuid-1111",
                original_file_name="conflow_requirement_spec.pdf",
                file_url="https://conflow.ai/storage/mock-spec.pdf",
                file_size=1024_580,
                file_extension="pdf",
                success=True,
                content=f"[Mock Parsing Content] '{question}'에 대한 답변 요약: 해당 문서에서 요구하는 태스크({task})에 부합하는 일정을 파싱 완료했습니다."  # noqa: E501
            )
        )
    else:
        # 주입된 file_info_list가 존재할 경우 매핑 파싱
        for info in info_list:
            output_results.append(
                FileSubgraphOutputState(
                    uuid=info.uuid,
                    original_file_name=info.original_file_name,
                    file_url=info.file_url,
                    file_size=info.file_size,
                    file_extension=info.file_extension,
                    success=True,
                    content=f"[Mock Engine] 파일 분석 완료. 태스크 규격 '{task}' 수행 및 사용자 질문 '{question}'에 기반한 텍스트 추출 완료."  # noqa: E501
                )
            )

    return {
        "file_process_results": output_results,
        "structured_response": {"status": "SUCCESS", "parsed_count": len(output_results)},
    }


def _llm_file_analysis(state: FileSubgraphState) -> dict[str, object]:
    """Structured LLM context merging with File Metadata."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "structured_response": {"status": "ERROR", "message": "OPENAI_API_KEY is missing"},
        }

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    info_list = state.file_info_list or []
    question = state.user_question or "이 파일의 핵심 요약을 제공해 주세요."
    task = state.file_task or "extract_and_process"

    system = SystemMessage(
        content=(
            "You are a Document Analysis RAG Agent for Conflow. "
            "Analyze the file metadata and answer the user's question or complete the task based on the assumed file content. "  # noqa: E501
            "Respond in concise Korean."
        )
    )
    human = HumanMessage(
        content=f"요청 태스크: {task}\n사용자 질문: {question}\n대상 파일 수: {len(info_list)}"
    )

    llm = ChatOpenAI(model=model_name, temperature=0.1)
    response = llm.invoke([system, human])

    output_results = []
    for info in info_list:
        output_results.append(
            FileSubgraphOutputState(
                uuid=info.uuid,
                original_file_name=info.original_file_name,
                file_url=info.file_url,
                file_size=info.file_size,
                file_extension=info.file_extension,
                success=True,
                content=str(response.content)
            )
        )

    return {
        "file_process_results": output_results,
        "structured_response": {"status": "SUCCESS", "engine": "gpt"},
    }


def validate_file_state(state: FileSubgraphState) -> dict[str, object]:
    """Fallback safe enforcement for state validation."""
    return {
        "user_question": state.user_question or "파일 분석 수행",
        "file_task": state.file_task or "extract"
    }


def route_after_validate(state: FileSubgraphState) -> Literal["analyze_document", "__end__"]:
    return "analyze_document"


def analyze_document(state: FileSubgraphState) -> dict[str, object]:
    mode = _resolve_agent_mode()
    if mode == "llm":
        return _llm_file_analysis(state)
    return _mock_file_analysis(state)


def build_graph() -> StateGraph:
    builder = StateGraph(FileSubgraphState)
    builder.add_node("validate_file_state", validate_file_state)
    builder.add_node("analyze_document", analyze_document)
    
    builder.add_edge(START, "validate_file_state")
    builder.add_conditional_edges(
        "validate_file_state",
        route_after_validate,
        {"analyze_document": "analyze_document", "__end__": END},
    )
    builder.add_edge("analyze_document", END)
    return builder


graph = build_graph().compile()
