"""User query analysis — intent routing for the supervisor graph."""

from __future__ import annotations

import os
import re
from typing import Any, Literal

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from src.app.core.shared import logger
from typing_extensions import TypedDict

URL_PATTERN = re.compile(
    r"https?://"
    r"(?:[^\s/?#]+)"
    r"(?:/[^\s?#]*)?"
    r"(?:\?[^\s#]*)?"
    r"(?:#[^\s]*)?",
    re.UNICODE,
)

RouteKey = Literal[
    "meeting_summary",
    "blocker_triage",
    "retro_insights",
    "file_analysis",
    "search",
    "FINISH",
]

_MEETING_SUMMARY_HINTS: tuple[str, ...] = (
    "meeting",
    "summary",
    "minutes",
    "minute",
    "standup",
    "stand-up",
    "huddle",
    "회의",
    "회의록",
    "미팅",
    "스탠드업",
    "전사",
    "허들",
    "요약해",
    "정리해",
)

_FILE_HINTS: tuple[str, ...] = (
    "file",
    "pdf",
    "docx",
    "document",
    "upload",
    "attachment",
    "파일",
    "첨부",
    "업로드",
    "문서 분석",
)

_SEARCH_HINTS: tuple[str, ...] = (
    "search",
    "find",
    "lookup",
    "rag",
    "retrieve",
    "검색",
    "찾아",
    "찾아줘",
    "조회",
    "레퍼런스",
)

_FILE_EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
    ".md",
)

_WORKER_DONE_MARKERS: tuple[str, ...] = (
    "summary complete",
    "mock output",
    "meeting_summary error",
    "blocker found",
    "insights generated",
    "file analysis complete",
    "search complete",
)


class UserQueryState(TypedDict, total=False):
    """State for the user_query graph and supervisor routing."""

    current_task: str
    agent_output: str
    chat_history: list[BaseMessage | dict[str, Any]]
    next_agent: RouteKey
    intent_text: str
    detected_urls: list[str]
    route_reason: str


class UserQueryClassification(BaseModel):
    """Structured LLM routing result (CONFLOW_AGENT_MODE=llm)."""

    route: RouteKey = Field(description="Worker graph to invoke next")
    reason: str = Field(
        max_length=512,
        description="Short justification in the same language as the user query",
    )


def extract_urls(text: str) -> list[str]:
    """Return unique HTTP(S) URLs found in *text*, in document order."""
    seen: set[str] = set()
    ordered: list[str] = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,);]")
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered


def message_content(message: BaseMessage | dict[str, Any]) -> str:
    """Extract text from a LangChain message or Studio JSON dict."""
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


def chat_text(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Join non-empty chat lines."""
    return "\n".join(
        text
        for message in chat_history
        if (text := message_content(message).strip())
    )


def task_from_chat(chat_history: list[BaseMessage | dict[str, Any]]) -> str:
    """Infer task text when the caller omits ``current_task``."""
    if not chat_history:
        return "Process the team collaboration request."
    return message_content(chat_history[-1]) or "Process the team collaboration request."


def build_intent_text(
    *,
    current_task: str,
    chat_history: list[BaseMessage | dict[str, Any]],
) -> str:
    """Combine explicit task and chat for classification."""
    chat = chat_text(chat_history)
    if chat and chat not in current_task:
        return f"{current_task}\n{chat}"
    return current_task


def _contains_hint(text: str, hints: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in hints)


def _urls_suggest_file(urls: list[str]) -> bool:
    return any(url.lower().split("?")[0].endswith(_FILE_EXTENSIONS) for url in urls)


def _worker_already_finished(agent_output: str) -> bool:
    output_lower = agent_output.lower()
    return any(marker in output_lower for marker in _WORKER_DONE_MARKERS)


def pick_route_rule_based(
    *,
    intent_text: str,
    agent_output: str,
    detected_urls: list[str] | None = None,
) -> tuple[RouteKey, str]:
    """Rule-based routing (default; no API key required)."""
    urls = detected_urls if detected_urls is not None else extract_urls(intent_text)

    if _worker_already_finished(agent_output):
        return "FINISH", "worker output indicates completion"

    if _contains_hint(intent_text, _MEETING_SUMMARY_HINTS):
        return "meeting_summary", "meeting summary keywords"

    if _contains_hint(intent_text, _FILE_HINTS) or _urls_suggest_file(urls):
        return "file_analysis", "file or document keywords / file URL"

    if _contains_hint(intent_text, _SEARCH_HINTS):
        return "search", "search / RAG keywords"

    intent_lower = intent_text.lower()

    if "blocker" in intent_lower and "blocker found" not in agent_output.lower():
        return "blocker_triage", "blocker keyword"

    if "retro" in intent_lower and "insights generated" not in agent_output.lower():
        return "retro_insights", "retro keyword"

    if urls and not _contains_hint(intent_text, _MEETING_SUMMARY_HINTS):
        return "search", "URL present without a stronger intent"

    return "FINISH", "no matching worker intent"


def _resolve_agent_mode() -> Literal["mock", "llm"]:
    raw = os.environ.get("CONFLOW_AGENT_MODE", "mock").strip().lower()
    return "llm" if raw == "llm" else "mock"


def pick_route_llm(
    *,
    intent_text: str,
    agent_output: str,
    detected_urls: list[str],
) -> tuple[RouteKey, str]:
    """LLM classification; falls back to rules on missing key or errors."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.warning("CONFLOW_AGENT_MODE=llm but OPENAI_API_KEY is missing; using rules")
        return pick_route_rule_based(
            intent_text=intent_text,
            agent_output=agent_output,
            detected_urls=detected_urls,
        )

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    system = SystemMessage(
        content=(
            "You route user requests for Conflow, a team collaboration assistant. "
            "Choose exactly one route: meeting_summary, blocker_triage, retro_insights, "
            "file_analysis, search, or FINISH. "
            "Use FINISH when the agent_output already contains a completed worker result "
            "or the request is unclear / chit-chat. "
            "Prefer meeting_summary for transcripts and minutes. "
            "Prefer file_analysis for uploaded documents. "
            "Prefer search for knowledge lookup. "
            "Do not invent facts."
        ),
    )
    human = HumanMessage(
        content=(
            f"User intent:\n{intent_text}\n\n"
            f"Detected URLs: {detected_urls or '(none)'}\n\n"
            f"Prior agent_output:\n{agent_output or '(empty)'}"
        ),
    )

    try:
        llm = ChatOpenAI(model=model_name, temperature=0.0)
        structured = llm.with_structured_output(UserQueryClassification)
        result: UserQueryClassification = structured.invoke([system, human])
        return result.route, result.reason
    except Exception as exc:
        logger.warning("LLM user_query routing failed: %s", exc)
        return pick_route_rule_based(
            intent_text=intent_text,
            agent_output=agent_output,
            detected_urls=detected_urls,
        )


def pick_route(
    *,
    current_task: str,
    agent_output: str,
    chat_history: list[BaseMessage | dict[str, Any]] | None = None,
    intent_text: str | None = None,
) -> tuple[RouteKey, str, list[str]]:
    """Resolve ``next_agent``, human-readable reason, and detected URLs."""
    task = (current_task or "").strip() or task_from_chat(chat_history or [])
    intent = intent_text or build_intent_text(
        current_task=task,
        chat_history=chat_history or [],
    )
    urls = extract_urls(intent)

    if _resolve_agent_mode() == "llm":
        route, reason = pick_route_llm(
            intent_text=intent,
            agent_output=agent_output,
            detected_urls=urls,
        )
    else:
        route, reason = pick_route_rule_based(
            intent_text=intent,
            agent_output=agent_output,
            detected_urls=urls,
        )

    return route, reason, urls


def analyze_user_query(
    state: UserQueryState,
    config: RunnableConfig,
) -> dict[str, Any]:
    """LangGraph node: classify user intent and set ``next_agent``."""
    del config  # reserved for future per-node model overrides

    current_task = (state.get("current_task") or "").strip() or task_from_chat(
        state.get("chat_history") or [],
    )
    agent_output = state.get("agent_output") or ""
    chat_history = list(state.get("chat_history") or [])
    intent = build_intent_text(current_task=current_task, chat_history=chat_history)
    next_agent, route_reason, urls = pick_route(
        current_task=current_task,
        agent_output=agent_output,
        chat_history=chat_history,
        intent_text=intent,
    )

    logger.info(
        "user_query route: %s — %s (urls=%d)",
        next_agent,
        route_reason,
        len(urls),
    )

    return {
        "current_task": current_task,
        "agent_output": agent_output,
        "chat_history": chat_history,
        "intent_text": intent,
        "detected_urls": urls,
        "route_reason": route_reason,
        "next_agent": next_agent,
    }


def build_graph() -> StateGraph:
    """Build the user_query StateGraph (uncompiled)."""
    builder = StateGraph(UserQueryState)
    builder.add_node("analyze_user_query", analyze_user_query)
    builder.add_edge(START, "analyze_user_query")
    builder.add_edge("analyze_user_query", END)
    return builder


graph = build_graph().compile()
