"""HTTP routes for LangGraph agent invocations."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from .graphs.meeting_summary import graph as meeting_summary_graph
from .graphs.schemas import MeetingSummaryInput, MeetingSummaryOutput

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/agent", tags=["agent"])


@router.post(
    "/meeting-summary",
    response_model=MeetingSummaryOutput,
    status_code=status.HTTP_200_OK,
    summary="Generate a structured meeting summary from a transcript",
)
async def create_meeting_summary(payload: MeetingSummaryInput) -> JSONResponse:
    """Invoke the LangGraph meeting_summary graph and return structured output."""
    try:
        result = meeting_summary_graph.invoke(
            {
                "meeting_title": payload.meeting_title,
                "transcript": payload.transcript,
                "team_context": payload.team_context,
            }
        )
    except Exception:
        logger.exception("meeting_summary graph failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Agent execution failed"},
        )

    if result.get("error"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": result["error"]},
        )

    output = MeetingSummaryOutput(
        overview=result.get("overview", ""),
        bullets=result.get("bullets", []),
        decisions=result.get("decisions", []),
        actions=result.get("actions", []),
        next_steps=result.get("next_steps", []),
    )
    return JSONResponse(
        content=output.model_dump(),
        status_code=status.HTTP_200_OK,
    )
