"""Agent Mode policy — single source of truth for LLM activation.

`CONFLOW_AGENT_MODE` env var (per docs/04-architecture/tech-stack.md):
    mock   — deterministic stubs, NO LLM calls (tests, CI, smoke)
    llm    — OpenAI (gpt-4o-mini default)
    ollama — local Ollama server
    vllm   — OpenAI-compatible vLLM endpoint

Worker code should never branch on the env var directly — call
`is_llm_active()` / `get_agent_mode()`. That way mode-switch policy stays
auditable and testable in one place.
"""

from __future__ import annotations

import enum
import os
from typing import Final


class AgentMode(enum.Enum):
    MOCK = "mock"
    LLM = "llm"
    OLLAMA = "ollama"
    VLLM = "vllm"


_ENV_VAR: Final = "CONFLOW_AGENT_MODE"


def get_agent_mode() -> AgentMode:
    """Read mode from env. Unknown values fall back to MOCK to keep
    accidental misconfigurations from hitting paid APIs."""
    raw = os.environ.get(_ENV_VAR, "mock").lower()
    try:
        return AgentMode(raw)
    except ValueError:
        return AgentMode.MOCK


def is_llm_active() -> bool:
    """True for any mode that actually issues LLM calls."""
    return get_agent_mode() != AgentMode.MOCK


def is_mock() -> bool:
    return get_agent_mode() == AgentMode.MOCK


__all__ = [
    "AgentMode",
    "get_agent_mode",
    "is_llm_active",
    "is_mock",
]
