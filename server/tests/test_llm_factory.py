"""Tests for the core LLM factory."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.core.llm_factory import get_huddle_llm, _resolve_mode  # noqa: E402, I001


def test_get_huddle_llm_defaults_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default mode stays offline and returns deterministic mock output."""
    monkeypatch.delenv("CONFLOW_AGENT_MODE", raising=False)

    llm = get_huddle_llm()
    result = llm.invoke([HumanMessage(content="회의록 정리해줘")])

    assert result.content.startswith("[mock]")


def test_resolve_mode_maps_local_to_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    """Legacy local mode aliases to the Ollama branch."""
    monkeypatch.setenv("CONFLOW_AGENT_MODE", "local")

    assert _resolve_mode() == "ollama"


def test_get_huddle_llm_vllm_mode_builds_chat_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """vLLM mode builds an OpenAI-compatible chat model without network calls."""
    monkeypatch.setenv("CONFLOW_AGENT_MODE", "vllm")
    monkeypatch.setenv("VLLM_BASE_URL", "http://localhost:8000/v1")
    monkeypatch.setenv("VLLM_MODEL", "qwen2.5:7b")
    monkeypatch.setenv("VLLM_API_KEY", "EMPTY")

    llm = get_huddle_llm(temperature=0.2)

    assert llm.__class__.__name__ == "ChatOpenAI"
