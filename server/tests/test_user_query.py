"""Tests for user_query intent routing (rule-based, no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.user_query import (  # noqa: E402
    analyze_user_query,
    extract_urls,
    pick_route,
    pick_route_rule_based,
)
from src.app.agent.graphs.user_query import (  # noqa: E402
    graph as user_query_graph,
)


@pytest.fixture(autouse=True)
def _force_mock_agent_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONFLOW_AGENT_MODE", "mock")


def test_extract_urls_dedupes_and_strips_trailing_punctuation() -> None:
    text = "See https://example.com/a.pdf, and https://example.com/a.pdf again."
    assert extract_urls(text) == ["https://example.com/a.pdf"]


def test_pick_route_meeting_summary_korean() -> None:
    route, reason, urls = pick_route(
        current_task="",
        agent_output="",
        chat_history=[{"type": "human", "content": "지난 허들 회의록 정리해줘"}],
    )
    assert route == "meeting_summary"
    assert "meeting" in reason.lower() or "회의" in reason or reason
    assert urls == []


def test_pick_route_file_analysis_from_extension() -> None:
    route, _, urls = pick_route(
        current_task="Analyze https://cdn.example.com/spec.pdf",
        agent_output="",
        chat_history=[],
    )
    assert route == "file_analysis"
    assert urls == ["https://cdn.example.com/spec.pdf"]


def test_pick_route_search_keywords() -> None:
    route, _, _ = pick_route(
        current_task="문서에서 인증 방식 검색해줘",
        agent_output="",
        chat_history=[],
    )
    assert route == "search"


def test_pick_route_finishes_after_worker_output() -> None:
    route, reason = pick_route_rule_based(
        intent_text="회의록 정리해줘",
        agent_output="summary complete\n\n한 줄 요약: ok",
    )
    assert route == "FINISH"
    assert "completion" in reason


def test_analyze_user_query_graph_node() -> None:
    result = analyze_user_query(
        {
            "chat_history": [
                {"type": "human", "content": "Please summarize the standup meeting."},
            ],
        },
        {},
    )
    assert result["next_agent"] == "meeting_summary"
    assert result["intent_text"]
    assert result["route_reason"]


def test_user_query_compiled_graph_invoke() -> None:
    result = user_query_graph.invoke(
        {
            "current_task": "blocker triage for sprint board",
            "agent_output": "",
            "chat_history": [],
        },
    )
    assert result["next_agent"] == "blocker_triage"
