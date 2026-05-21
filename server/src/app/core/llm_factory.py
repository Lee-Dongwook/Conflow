"""Factory for creating LLM instances with guardrails."""

from __future__ import annotations

import os
from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.messages import BaseMessage

DEFAULT_MODEL_NAME = "gpt-4o-mini"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_VLLM_BASE_URL = "http://localhost:8000/v1"
SUPPORTED_MODES = {"mock", "llm", "ollama", "vllm", "local"}


class MockHuddleChatModel(SimpleChatModel):
    """Deterministic stand-in used while the app runs in mock mode."""

    temperature: float = 0.1
    model_name: str = "mock-huddle"

    @property
    def _llm_type(self) -> str:
        return "mock-huddle"

    def _call(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: object | None = None,
        **kwargs: object,
    ) -> str:
        for message in reversed(messages):
            content = str(getattr(message, "content", "")).strip()
            if content:
                return f"[mock] {content[:160]}"
        return "[mock] huddle response"


def _resolve_mode() -> Literal["mock", "llm", "ollama", "vllm"]:
    """Normalize ``CONFLOW_AGENT_MODE`` into a supported execution mode."""
    raw_mode = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()
    if raw_mode == "local":
        return "ollama"
    if raw_mode in SUPPORTED_MODES:
        return raw_mode
    return "mock"


def _load_chat_openai() -> type[BaseChatModel]:
    """Import ChatOpenAI lazily so mock mode stays import-safe."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI


def _load_chat_ollama() -> type[BaseChatModel]:
    """Import ChatOllama lazily with a fallback to the community package."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        try:
            from langchain_community.chat_models import ChatOllama
        except ImportError as second_error:  # pragma: no cover - environment-specific
            raise ImportError(
                "Ollama mode requires either 'langchain-ollama' or 'langchain-community'.",
            ) from second_error
    return ChatOllama


def _build_openai_llm(temperature: float) -> BaseChatModel:
    """Return a ChatOpenAI instance for remote OpenAI-compatible providers."""
    ChatOpenAI = _load_chat_openai()
    model_name = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL_NAME).strip() or DEFAULT_MODEL_NAME
    return ChatOpenAI(model=model_name, temperature=temperature)


def _build_ollama_llm(temperature: float) -> BaseChatModel:
    """Return a ChatOllama instance for local Ollama inference."""
    ChatOllama = _load_chat_ollama()
    model_name = (
        os.environ.get("OLLAMA_MODEL")
        or os.environ.get("LOCAL_MODEL")
        or "qwen2.5:7b"
    ).strip()
    base_url = (
        os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).strip()
        or DEFAULT_OLLAMA_BASE_URL
    )
    return ChatOllama(model=model_name, base_url=base_url, temperature=temperature)


def _build_vllm_llm(temperature: float) -> BaseChatModel:
    """Return a ChatOpenAI instance configured for an OpenAI-compatible vLLM server."""
    ChatOpenAI = _load_chat_openai()
    model_name = (
        os.environ.get("VLLM_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or DEFAULT_MODEL_NAME
    ).strip()
    base_url = (
        os.environ.get("VLLM_BASE_URL", DEFAULT_VLLM_BASE_URL).strip()
        or DEFAULT_VLLM_BASE_URL
    )
    api_key = os.environ.get("VLLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "EMPTY"
    return ChatOpenAI(model=model_name, base_url=base_url, api_key=api_key, temperature=temperature)


def get_huddle_llm(temperature: float = 0.1) -> BaseChatModel:
    """Create the huddle LLM for the current runtime mode.

    Mock mode is the default so local development stays offline and import-safe.
    """
    mode = _resolve_mode()

    if mode == "llm":
        return _build_openai_llm(temperature)
    if mode == "ollama":
        return _build_ollama_llm(temperature)
    if mode == "vllm":
        return _build_vllm_llm(temperature)
    return MockHuddleChatModel(temperature=temperature)
