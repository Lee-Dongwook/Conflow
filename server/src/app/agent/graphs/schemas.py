"""Pydantic schemas for agent graph I/O (A2UI-aligned with MeetingSummaryPage)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MeetingActionItem(BaseModel):
    """Single action extracted from a meeting."""

    task: str = Field(min_length=1, max_length=512)
    owner: str = Field(default="미정", max_length=128)


class MeetingSummaryOutput(BaseModel):
    """Structured meeting summary — mirrors apps/web MeetingSummaryPage detail shape."""

    overview: str = Field(description="한 줄 요약")
    bullets: list[str] = Field(default_factory=list, description="핵심 논의")
    decisions: list[str] = Field(default_factory=list, description="결정 사항")
    actions: list[MeetingActionItem] = Field(default_factory=list, description="액션")
    next_steps: list[str] = Field(default_factory=list, description="다음 단계")


class MeetingSummaryInput(BaseModel):
    """Input accepted by the meeting_summary graph."""

    meeting_title: str = Field(min_length=1, max_length=256)
    transcript: str = Field(min_length=1)
    team_context: str | None = Field(
        default=None,
        description="팀/스프린트 맥락 (예: 대학 스터디, 1주 스프린트)",
    )


AgentMode = Literal["mock", "llm"]
