"""Factory for creating LLM instances with guardrails."""

import os

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


def get_huddle_llm(temperature: float = 0.1):
    mode = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()

    if mode == "llm":
        model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model_name, temperature=temperature)
    
    elif mode == "local":
        local_model = os.environ.get("LOCAL_MODEL", "qwen2.5:7b")
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

        return ChatOllama(
            model=local_model,
            base_url=ollama_url,
            temperature=0.0
        )

    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
