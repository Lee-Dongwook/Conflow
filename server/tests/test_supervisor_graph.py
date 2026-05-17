"""Tests for supervisor_graph (mock meeting_summary, no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.sample_transcript import SAMPLE_TRANSCRIPT  # noqa: E402
from src.app.agent.graphs.supervisor_graph import supervisor_agent_graph  # noqa: E402


@pytest.fixture(autouse=True)
def _force_mock_agent_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure meeting_summary child graph stays on mock path."""
    monkeypatch.setenv("CONFLOW_AGENT_MODE", "mock")


def test_supervisor_invokes_meeting_summary_graph() -> None:
    """Supervisor routes to meeting_summary and returns structured fields."""
    result = supervisor_agent_graph.invoke(
        {
            "current_task": "Generate a meeting summary for the last standup.",
            "agent_output": "",
            "transcript": SAMPLE_TRANSCRIPT,
            "meeting_title": "FE 스터디 — 스프린트 계획",
            "chat_history": [
                {"type": "human", "content": "Please summarize the standup meeting."},
            ],
        },
    )

    assert result.get("next_agent") == "FINISH"
    assert "summary complete" in (result.get("agent_output") or "").lower()
    assert result.get("overview")
    assert isinstance(result.get("bullets"), list)
    assert len(result["bullets"]) > 0


def test_supervisor_uses_sample_transcript_when_chat_is_short() -> None:
    """Short Studio prompt falls back to sample transcript for mock summarize."""
    result = supervisor_agent_graph.invoke(
        {
            "current_task": "Generate a meeting summary for the last standup.",
            "chat_history": [
                {"type": "human", "content": "Please summarize the standup meeting."},
            ],
        },
    )

    assert result.get("next_agent") == "FINISH"
    assert "summary complete" in (result.get("agent_output") or "").lower()
    assert SAMPLE_TRANSCRIPT[:20] in (result.get("transcript") or "")


def test_natural_language_meeting_minutes_english() -> None:
    """'meeting minutes' style instruction routes without current_task."""
    result = supervisor_agent_graph.invoke(
        {
            "chat_history": [
                {
                    "type": "human",
                    "content": "Please prepare meeting minutes from the last team sync.",
                },
            ],
        },
    )

    assert result.get("next_agent") == "FINISH"
    assert result.get("overview")
    assert "summary complete" in (result.get("agent_output") or "").lower()


def test_natural_language_meeting_minutes_korean() -> None:
    """회의록/허들 같은 한국어 지시만으로 meeting_summary 실행."""
    result = supervisor_agent_graph.invoke(
        {
            "chat_history": [
                {"type": "human", "content": "지난 허들 회의록 정리해줘"},
            ],
        },
    )

    assert result.get("next_agent") == "FINISH"
    assert result.get("overview")
    assert len(result.get("bullets") or []) > 0


def _collect_stream_node_names(chunks: object) -> set[str]:
    """Flatten parent + subgraph node names from stream chunks."""
    names: set[str] = set()
    for chunk in chunks:
        payload = chunk[1] if isinstance(chunk, tuple) else chunk
        if not isinstance(payload, dict):
            continue
        for key, value in payload.items():
            names.add(key)
            if isinstance(value, dict):
                names.update(value.keys())
    return names


def test_supervisor_stream_exposes_meeting_summary_subgraph_nodes() -> None:
    """Subgraph node emits validate_input / summarize when stream(subgraphs=True)."""
    chunks = list(
        supervisor_agent_graph.stream(
            {
                "current_task": "회의록 만들어줘",
                "transcript": SAMPLE_TRANSCRIPT,
                "chat_history": [{"type": "human", "content": "이 전사로 회의록 만들어줘"}],
            },
            subgraphs=True,
        ),
    )
    node_names = _collect_stream_node_names(chunks)

    assert "prepare_meeting_summary" in node_names
    assert "meeting_summary" in node_names
    assert "finalize_meeting_summary" in node_names
    assert "validate_input" in node_names
    assert "summarize" in node_names


def test_supervisor_infers_task_from_chat_only() -> None:
    """Studio-style input without current_task still works."""
    result = supervisor_agent_graph.invoke(
        {
            "transcript": SAMPLE_TRANSCRIPT,
            "chat_history": [
                {"type": "human", "content": "Summarize our sprint planning meeting."},
            ],
        },
    )

    assert result.get("current_task")
    assert "sprint planning" in result["current_task"].lower()
    assert result.get("overview")
