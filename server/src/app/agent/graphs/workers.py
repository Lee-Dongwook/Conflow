"""Worker graph invocations (supervisor → child graphs)."""

from __future__ import annotations

from typing import Any

from src.app.agent.graphs.meeting_summary import graph as meeting_summary_graph
from src.app.agent.graphs.sample_transcript import SAMPLE_TRANSCRIPT


def invoke_meeting_summary(
    *,
    meeting_title: str,
    transcript: str,
    team_context: str | None = None,
) -> dict[str, Any]:
    """Run the meeting_summary graph (respects CONFLOW_AGENT_MODE mock/llm)."""
    return meeting_summary_graph.invoke(
        {
            "meeting_title": meeting_title,
            "transcript": transcript,
            "team_context": team_context,
        },
    )


def format_meeting_summary_for_supervisor(result: dict[str, Any]) -> str:
    """Flatten meeting_summary state into agent_output text for routing."""
    if result.get("error"):
        return f"meeting_summary error: {result['error']}"

    overview = result.get("overview") or ""
    bullets = result.get("bullets") or []
    decisions = result.get("decisions") or []
    actions = result.get("actions") or []
    next_steps = result.get("next_steps") or []

    lines = ["summary complete", "", f"한 줄 요약: {overview}"]

    if bullets:
        lines.extend(["", "핵심 논의:"])
        lines.extend(f"- {b}" for b in bullets)

    if decisions:
        lines.extend(["", "결정:"])
        lines.extend(f"- {d}" for d in decisions)

    if actions:
        lines.extend(["", "액션:"])
        for action in actions:
            task = action.get("task", "")
            owner = action.get("owner", "미정")
            lines.append(f"- {task} (@{owner})")

    if next_steps:
        lines.extend(["", "다음 단계:"])
        lines.extend(f"- {n}" for n in next_steps)

    return "\n".join(lines)


def default_transcript_when_missing(chat_text: str) -> str:
    """Use chat text if long enough; otherwise sample transcript for local dev."""
    stripped = chat_text.strip()
    if len(stripped) >= 40:
        return stripped
    return SAMPLE_TRANSCRIPT
