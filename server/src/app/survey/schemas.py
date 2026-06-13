from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

RespondentRole = Literal[
    "capstone_leader",
    "capstone_member",
    "club_operator",
    "club_member",
    "startup_founder",
    "side_project_leader",
    "other",
]


class SurveySubmit(BaseModel):
    """Payload for submitting an anonymous survey response."""

    survey_key: str = Field(min_length=1, max_length=64)
    respondent_role: RespondentRole
    organization: str | None = Field(default=None, max_length=200)
    contact_email: EmailStr | None = None
    consents_to_followup: bool = False
    answers: dict[str, Any] = Field(default_factory=dict)


class SurveyResponseRead(BaseModel):
    """Read model for a survey response (admin/aggregation)."""

    uuid: str
    created_at: datetime
    survey_key: str
    respondent_role: str
    organization: str | None = None
    contact_email: str | None = None
    consents_to_followup: bool
    answers: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class SurveyAggregateRead(BaseModel):
    """Aggregated counts for a survey_key, broken down by role."""

    survey_key: str
    total: int
    by_role: dict[str, int]
    follow_up_consents: int
