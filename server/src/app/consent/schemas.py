from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .model import ConsentType


class ConsentAccept(BaseModel):
    """Payload for recording a consent acceptance."""

    consent_type: ConsentType
    version: str


class ConsentBatchAccept(BaseModel):
    """Payload for recording multiple consents at once (signup flow)."""

    consents: list[ConsentAccept]


class ConsentRead(BaseModel):
    """Read model for a consent record."""

    uuid: str
    user_uuid: str
    consent_type: ConsentType
    version: str
    accepted_at: datetime
    revoked_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConsentStatusRead(BaseModel):
    """Aggregated consent status for a user."""

    terms: ConsentRead | None = None
    privacy: ConsentRead | None = None
    third_party: ConsentRead | None = None
    marketing: ConsentRead | None = None
    all_required_accepted: bool = False


CURRENT_VERSIONS = {
    ConsentType.TERMS: "1.0",
    ConsentType.PRIVACY: "1.0",
    ConsentType.THIRD_PARTY: "1.0",
    ConsentType.MARKETING: "1.0",
}

REQUIRED_CONSENTS = frozenset({
    ConsentType.TERMS,
    ConsentType.PRIVACY,
    ConsentType.THIRD_PARTY,
})
