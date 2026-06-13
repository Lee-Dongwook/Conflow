from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..common.models import AutoUUIDMixin
from ..core.database import Base


class SurveyResponse(Base, AutoUUIDMixin):
    """Anonymous survey response collected during Phase 0 hypothesis validation.

    Schema kept intentionally flexible: structured columns for aggregation
    (role, organization), JSONB for question answers that iterate weekly.
    """

    __tablename__ = "survey_responses"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    survey_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    respondent_role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    consents_to_followup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    answers: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
