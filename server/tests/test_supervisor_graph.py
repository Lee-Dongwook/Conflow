"""Tests for supervisor_graph (no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.supervisor_graph import supervisor_agent_graph  # noqa: E402


def test_supervisor_meeting_summary_flow() -> None:
    """Standup summary input runs without KeyError and reaches worker mock."""
    result = supervisor_agent_graph.invoke(
        {
            "current_task": "Generate a meeting summary for the last standup.",
            "agent_output": "",
            "chat_history": [
                {"type": "human", "content": "Please summarize the standup meeting."},
            ],
        },
    )

    assert result.get("current_task")
    assert "mock output" in (result.get("agent_output") or "").lower()
    assert result.get("next_agent") == "FINISH"


def test_supervisor_infers_task_from_chat_only() -> None:
    """Studio-style input without current_task still works."""
    result = supervisor_agent_graph.invoke(
        {
            "chat_history": [
                {"type": "human", "content": "Summarize our sprint planning meeting."},
            ],
        },
    )

    assert result.get("current_task")
    assert "sprint planning" in result["current_task"].lower()
