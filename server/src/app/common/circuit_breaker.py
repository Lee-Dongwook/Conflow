"""Circuit Breaker Utility for External AI APIs."""

from __future__ import annotations

import logging
from typing import Any

import pybreaker
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

llm_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    name="OpenAI-API-Breaker"  
)

class LogCircuitBreakerListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        logger.error(f"[CIRCUIT BREAKER] State changed from {old_state.name} to {new_state.name}")

llm_circuit_breaker.add_listener(LogCircuitBreakerListener())

async def execute_llm_with_circuit_breaker(
    primary_llm: ChatOpenAI,
    fallback_mode_model_name: str,
    messages: list[BaseMessage],
    structured_schema: Any = None
) -> Any:
    try:
        if not llm_circuit_breaker.current_state.name == "open":
            target_llm = primary_llm.with_structured_output(structured_schema) if structured_schema else primary_llm  # noqa: E501

            try:
                result = await llm_circuit_breaker.call(target_llm.ainvoke, messages)
                return result
            except Exception as e:
                llm_circuit_breaker.handle_failure(e)
                return e
        else:
            raise pybreaker.CircuitBreakerOpenException()

    except (Exception, pybreaker.CircuitBreakerOpenException) as e:
        logger.warning(f"Circuit Breaker activated or API error occurred: {str(e)}")
        logger.warning(f"Automatically falling back to local infrastructure model: {fallback_mode_model_name}")  # noqa: E501

        from langchain_community.chat_models import ChatOllama
        fallback_llm = ChatOllama(model=fallback_mode_model_name, temperature=0.0)

        if structured_schema:
            fallback_llm = fallback_llm.with_structured_output(structured_schema)
        
        return await fallback_llm.ainvoke(messages)
