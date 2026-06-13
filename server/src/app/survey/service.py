from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import SurveyResponse
from .schemas import SurveyAggregateRead, SurveySubmit


async def submit_response(
    db: AsyncSession,
    *,
    payload: SurveySubmit,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> SurveyResponse:
    record = SurveyResponse(
        survey_key=payload.survey_key,
        respondent_role=payload.respondent_role,
        organization=payload.organization,
        contact_email=str(payload.contact_email) if payload.contact_email else None,
        consents_to_followup=payload.consents_to_followup,
        answers=payload.answers,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(record)
    await db.flush()
    return record


async def list_responses(
    db: AsyncSession,
    *,
    survey_key: str | None = None,
    limit: int = 200,
) -> list[SurveyResponse]:
    stmt = select(SurveyResponse).order_by(SurveyResponse.created_at.desc()).limit(limit)
    if survey_key:
        stmt = stmt.where(SurveyResponse.survey_key == survey_key)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def aggregate_by_role(
    db: AsyncSession,
    *,
    survey_key: str,
) -> SurveyAggregateRead:
    role_stmt = (
        select(SurveyResponse.respondent_role, func.count(SurveyResponse.uuid))
        .where(SurveyResponse.survey_key == survey_key)
        .group_by(SurveyResponse.respondent_role)
    )
    role_rows = (await db.execute(role_stmt)).all()
    by_role = {row[0]: row[1] for row in role_rows}
    total = sum(by_role.values())

    follow_up_stmt = select(func.count(SurveyResponse.uuid)).where(
        SurveyResponse.survey_key == survey_key,
        SurveyResponse.consents_to_followup.is_(True),
    )
    follow_up_count = (await db.execute(follow_up_stmt)).scalar_one()

    return SurveyAggregateRead(
        survey_key=survey_key,
        total=total,
        by_role=by_role,
        follow_up_consents=follow_up_count,
    )
