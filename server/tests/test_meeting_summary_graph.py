"""Tests for meeting_summary LangGraph (mock mode, no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.meeting_summary import graph  # noqa: E402
from src.app.agent.graphs.sample_transcript import (  # noqa: E402
    SAMPLE_MEETING_TITLE,
    SAMPLE_TRANSCRIPT,
)


def test_meeting_summary_mock_produces_structured_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mock mode returns overview, bullets, and no error."""
    monkeypatch.setenv("CONFLOW_AGENT_MODE", "mock")

    result = graph.invoke(
        {
            "meeting_title": SAMPLE_MEETING_TITLE,
            "transcript": SAMPLE_TRANSCRIPT,
        },
    )

    assert result.get("error") is None
    assert isinstance(result.get("overview"), str)
    assert len(result["overview"]) > 0
    assert isinstance(result.get("bullets"), list)
    assert result.get("agent_mode") == "mock"


def test_meeting_summary_rejects_empty_transcript() -> None:
    """Validation fails when transcript is missing."""
    result = graph.invoke(
        {
            "meeting_title": "테스트",
            "transcript": "   ",
        },
    )

    assert result.get("error") == "transcript is required"
