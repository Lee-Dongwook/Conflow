#!/usr/bin/env python3
"""Run supervisor_graph (user_query + workers) without LangGraph dev server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.sample_transcript import (  # noqa: E402
    SAMPLE_MEETING_TITLE,
    SAMPLE_TRANSCRIPT,
)
from src.app.agent.graphs.supervisor_graph import supervisor_agent_graph  # noqa: E402

PRESETS: dict[str, dict[str, Any]] = {
    "meeting": {
        "current_task": "Generate a meeting summary for the last standup.",
        "transcript": SAMPLE_TRANSCRIPT,
        "meeting_title": SAMPLE_MEETING_TITLE,
        "chat_history": [
            {"type": "human", "content": "Please summarize the standup meeting."},
        ],
    },
    "meeting-chat-only": {
        "chat_history": [
            {"type": "human", "content": "지난 허들 회의록 정리해줘"},
        ],
    },
    "file": {
        "chat_history": [
            {
                "type": "human",
                "content": "https://cdn.example.com/spec.pdf 파일 분석해줘",
            },
        ],
    },
    "search": {
        "chat_history": [
            {"type": "human", "content": "Conflow 문서에서 OAuth 설정 검색해줘"},
        ],
    },
    "finish": {
        "current_task": "Hello",
        "chat_history": [{"type": "human", "content": "안녕"}],
    },
}


def _routing_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "next_agent": result.get("next_agent"),
        "route_reason": result.get("route_reason"),
        "intent_text": result.get("intent_text"),
        "detected_urls": result.get("detected_urls"),
        "agent_output_preview": (result.get("agent_output") or "")[:240],
        "overview": result.get("overview"),
        "bullets_count": len(result.get("bullets") or []),
    }


def _collect_stream_nodes(chunks: list[Any]) -> set[str]:
    names: set[str] = set()
    for chunk in chunks:
        payload = chunk[1] if isinstance(chunk, tuple) else chunk
        if not isinstance(payload, dict):
            continue
        for key, value in payload.items():
            names.add(key)
            if isinstance(value, dict):
                names.update(value.keys())
    return names


def run_invoke(preset: str, payload: dict[str, Any]) -> None:
    result = supervisor_agent_graph.invoke(payload)
    print(f"\n=== invoke preset={preset} ===")
    print(json.dumps(_routing_summary(result), ensure_ascii=False, indent=2))


def run_stream(preset: str, payload: dict[str, Any]) -> None:
    chunks = list(supervisor_agent_graph.stream(payload, subgraphs=True))
    nodes = sorted(_collect_stream_nodes(chunks))
    print(f"\n=== stream preset={preset} (subgraphs=True) ===")
    print("nodes:", ", ".join(nodes))


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test supervisor_graph")
    parser.add_argument(
        "--preset",
        choices=[*sorted(PRESETS), "all"],
        default="meeting",
        help="Input preset or 'all' (default: meeting)",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Also print subgraph node names from stream()",
    )
    args = parser.parse_args()

    presets = sorted(PRESETS) if args.preset == "all" else [args.preset]

    for name in presets:
        payload = PRESETS[name]
        run_invoke(name, payload)
        if args.stream:
            run_stream(name, payload)


if __name__ == "__main__":
    main()
