"""Structured Output Guardrail with Self-Correction Mechanism."""

from __future__ import annotations

import json
import logging
from typing import TypeVar

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from src.app.common.circuit_breaker import execute_llm_with_circuit_breaker

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

async def call_llm_with_guardrails(  # noqa: UP047
    llm: ChatOpenAI,
    schema: type[T],
    messages: list[BaseMessage],
    max_retries: int = 3,
) -> T:
    current_messages = messages.copy()

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt} of {max_retries} to call LLM with guardrails")
            result = await execute_llm_with_circuit_breaker(
                primary_llm=llm,
                fallback_mode_model_name="qwen2.5:7b",
                messages=current_messages,
                structured_schema=schema
            )

            if result is None:
                raise ValueError("LLM이 지정된 구조화 스키마에 부합하는 데이터를 생성하지 못하고 빈 값을 반환했습니다.")  # noqa: E501

            return result
        
        except (ValidationError, ValueError, json.JSONDecodeError, TypeError) as e:
            logger.warning("Guardrail activated: Schema violation detected on attempt %d. Error: %s", attempt, e)  # noqa: E501

            if attempt == max_retries:
                logger.error("Max retries reached. Failed to generate valid output after %d attempts.", max_retries)  # noqa: E501
                raise e
            
            error_feedback = (
                f"\n\n[SYSTEM ERROR]: 당신이 방금 전에 반환한 응답은 지정된 Pydantic 스키마 검증을 통과하지 못했습니다.\n"  # noqa: E501
                f"■ 발생한 검증 에러 내용:\n{str(e)}\n\n"
                f"요구사항과 필드 제약 조건을 다시 엄격히 검토한 뒤, 오류를 수정한 완벽한 JSON 구조로만 다시 응답하십시오."  # noqa: E501
            )

            current_messages.append(HumanMessage(content=error_feedback))
