"""HTTP routes for user consent management."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .model import ConsentType
from .schemas import ConsentBatchAccept, ConsentRead, ConsentStatusRead
from .service import (
    accept_consents_batch,
    get_consent_history,
    get_consent_status,
    revoke_consent,
)

router = APIRouter(prefix="/consents", tags=["consents"])


@router.get("/status", response_model=ConsentStatusRead)
async def get_my_consent_status(
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> ConsentStatusRead:
    """Get current user's consent status for all types."""
    return await get_consent_status(db, current_user.uuid)


@router.get("/history", response_model=list[ConsentRead])
async def get_my_consent_history(
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> list[ConsentRead]:
    """Get full consent history for the current user."""
    records = await get_consent_history(db, current_user.uuid)
    return [ConsentRead.model_validate(r) for r in records]


@router.post("/accept", response_model=list[ConsentRead], status_code=status.HTTP_201_CREATED)
async def accept_consents_route(
    payload: ConsentBatchAccept,
    request: Request,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> list[ConsentRead]:
    """Record consent acceptances (supports batch for signup flow)."""
    ip = request.client.host if request.client else None
    records = await accept_consents_batch(
        db,
        user_uuid=current_user.uuid,
        consents=payload.consents,
        ip_address=ip,
    )
    return [ConsentRead.model_validate(r) for r in records]


@router.delete("/{consent_type}", response_model=ConsentRead)
async def revoke_consent_route(
    consent_type: ConsentType,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
) -> ConsentRead:
    """Revoke a specific consent (e.g., marketing)."""
    record = await revoke_consent(
        db,
        user_uuid=current_user.uuid,
        consent_type=consent_type,
    )
    if not record:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active consent found for type: {consent_type.value}",
        )
    return ConsentRead.model_validate(record)
