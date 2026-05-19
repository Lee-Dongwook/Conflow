#!/usr/bin/env python3
"""Run user_query graph once (intent routing, mock mode by default)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.user_query import graph  # noqa: E402

PRESETS: dict[str, dict[str, object]] = {
    "meeting": {
        "chat_history": [
            {"type": "human", "content": "지난 허들 회의록 정리해줘"},
        ],
    },
    "file": {
        "current_task": "Analyze https://cdn.example.com/spec.pdf",
        "chat_history": [],
    },
    "search": {
        "current_task": "문서에서 인증 방식 검색해줘",
        "chat_history": [],
    },
    "blocker": {
        "current_task": "List blockers on the sprint board",
        "chat_history": [],
    },
}


def main() -> None:
    """Invoke user_query graph and print routing JSON."""
    parser = argparse.ArgumentParser(description="Smoke-test user_query graph")
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default="meeting",
        help="Built-in input preset (default: meeting)",
    )
    args = parser.parse_args()

    payload = PRESETS[args.preset]
    result = graph.invoke(payload)

    print(f"--- preset={args.preset} ---")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
