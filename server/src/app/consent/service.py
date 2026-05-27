from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import ConsentType, UserConsent
from .schemas import (
    CURRENT_VERSIONS,
    REQUIRED_CONSENTS,
    ConsentAccept,
    ConsentRead,
    ConsentStatusRead,
)


async def accept_consent(
    db: AsyncSession,
    *,
    user_uuid: str,
    consent: ConsentAccept,
    ip_address: str | None = None,
) -> UserConsent:
    record = UserConsent(
        user_uuid=user_uuid,
        consent_type=consent.consent_type,
        version=consent.version,
        ip_address=ip_address,
    )
    db.add(record)
    await db.flush()
    return record


async def accept_consents_batch(
    db: AsyncSession,
    *,
    user_uuid: str,
    consents: list[ConsentAccept],
    ip_address: str | None = None,
) -> list[UserConsent]:
    records = []
    for consent in consents:
        record = UserConsent(
            user_uuid=user_uuid,
            consent_type=consent.consent_type,
            version=consent.version,
            ip_address=ip_address,
        )
        db.add(record)
        records.append(record)
    await db.flush()
    return records


async def revoke_consent(
    db: AsyncSession,
    *,
    user_uuid: str,
    consent_type: ConsentType,
) -> UserConsent | None:
    stmt = (
        select(UserConsent)
        .where(
            UserConsent.user_uuid == user_uuid,
            UserConsent.consent_type == consent_type,
            UserConsent.revoked_at.is_(None),
        )
        .order_by(UserConsent.accepted_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if record:
        record.revoked_at = datetime.now(UTC)
        await db.flush()
    return record


async def get_latest_consents(
    db: AsyncSession,
    user_uuid: str,
) -> dict[ConsentType, UserConsent]:
    stmt = (
        select(UserConsent)
        .where(
            UserConsent.user_uuid == user_uuid,
            UserConsent.revoked_at.is_(None),
        )
        .order_by(UserConsent.accepted_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    latest: dict[ConsentType, UserConsent] = {}
    for row in rows:
        if row.consent_type not in latest:
            latest[row.consent_type] = row
    return latest


async def get_consent_status(
    db: AsyncSession,
    user_uuid: str,
) -> ConsentStatusRead:
    latest = await get_latest_consents(db, user_uuid)

    def _to_read(ct: ConsentType) -> ConsentRead | None:
        record = latest.get(ct)
        if not record:
            return None
        return ConsentRead.model_validate(record)

    all_required = all(
        ct in latest and latest[ct].version == CURRENT_VERSIONS[ct]
        for ct in REQUIRED_CONSENTS
    )

    return ConsentStatusRead(
        terms=_to_read(ConsentType.TERMS),
        privacy=_to_read(ConsentType.PRIVACY),
        third_party=_to_read(ConsentType.THIRD_PARTY),
        marketing=_to_read(ConsentType.MARKETING),
        all_required_accepted=all_required,
    )


async def get_consent_history(
    db: AsyncSession,
    user_uuid: str,
) -> list[UserConsent]:
    stmt = (
        select(UserConsent)
        .where(UserConsent.user_uuid == user_uuid)
        .order_by(UserConsent.accepted_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
