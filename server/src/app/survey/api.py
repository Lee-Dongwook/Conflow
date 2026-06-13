"""HTTP routes for anonymous survey submission and aggregation."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import (
    SurveyAggregateRead,
    SurveyResponseRead,
    SurveySubmit,
)
from .service import (
    aggregate_by_role,
    list_responses,
    submit_response,
)

router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.post(
    "/responses",
    response_model=SurveyResponseRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_survey_response(
    payload: SurveySubmit,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> SurveyResponseRead:
    """Anonymous survey submission. No authentication required."""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    if user_agent and len(user_agent) > 512:
        user_agent = user_agent[:512]
    record = await submit_response(
        db,
        payload=payload,
        ip_address=ip,
        user_agent=user_agent,
    )
    return SurveyResponseRead.model_validate(record)


@router.get(
    "/responses",
    response_model=list[SurveyResponseRead],
)
async def list_survey_responses(
    survey_key: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> list[SurveyResponseRead]:
    """List survey responses (authenticated, for analysis)."""
    records = await list_responses(db, survey_key=survey_key, limit=limit)
    return [SurveyResponseRead.model_validate(r) for r in records]


@router.get(
    "/aggregate",
    response_model=SurveyAggregateRead,
)
async def aggregate_survey(
    survey_key: str = Query(..., min_length=1),
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> SurveyAggregateRead:
    """Aggregate counts for a survey_key, broken down by respondent role."""
    return await aggregate_by_role(db, survey_key=survey_key)
