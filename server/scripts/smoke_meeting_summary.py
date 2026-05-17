#!/usr/bin/env python3
"""Run meeting_summary graph once without LangGraph dev server."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.app.agent.graphs.meeting_summary import graph  # noqa: E402
from src.app.agent.graphs.sample_transcript import (  # noqa: E402
    SAMPLE_MEETING_TITLE,
    SAMPLE_TEAM_CONTEXT,
    SAMPLE_TRANSCRIPT,
)


def main() -> None:
    """Invoke graph with sample transcript and print JSON."""
    result = graph.invoke(
        {
            "meeting_title": SAMPLE_MEETING_TITLE,
            "transcript": SAMPLE_TRANSCRIPT,
            "team_context": SAMPLE_TEAM_CONTEXT,
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
