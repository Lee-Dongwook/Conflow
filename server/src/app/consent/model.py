from __future__ import annotations

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.models import AutoUUIDMixin
from ..core.database import Base

if TYPE_CHECKING:
    from ..user.model import User


class ConsentType(enum.Enum):
    TERMS = "terms"
    PRIVACY = "privacy"
    THIRD_PARTY = "third_party"
    MARKETING = "marketing"


class UserConsent(Base, AutoUUIDMixin):
    """Records a user's consent acceptance for a specific document version."""

    __tablename__ = "user_consents"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        nullable=False,
    )

    user_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid"),
        nullable=False,
        index=True,
    )

    consent_type: Mapped[ConsentType] = mapped_column(
        Enum(
            ConsentType,
            name="consenttype",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(String(20), nullable=False)

    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="consents")
