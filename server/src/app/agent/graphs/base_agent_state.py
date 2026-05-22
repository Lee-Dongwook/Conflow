from typing import Literal, TypedDict

from langchain_core.messages import BaseMessage

RouteKey = Literal[
    "meeting_summary",
    "blocker_triage",
    "retro_insights",
    "file_analysis",
    "search",
    "FINISH",
]


class AgentState(TypedDict, total=False):
    """Supervisor state; shared with user_query and meeting_summary subgraphs."""

    current_task: str
    agent_output: str
    chat_history: list[BaseMessage]
    summary: str
    next_agent: RouteKey
    meeting_title: str
    transcript: str
    team_context: str | None
    overview: str
    bullets: list[str]
    decisions: list[str]
    actions: list[dict[str, str]]
    next_steps: list[str]
    agent_mode: str | None
    error: str | None
    intent_text: str
    detected_urls: list[str]
    route_reason: str
    user_feedback: Literal["approve", "reject"] | None
    review_comment: str | None
