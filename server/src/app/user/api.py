"""HTTP routes for user CRUD operations."""
import logging
import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verfiy_token import get_access_token
from .lib import get_cookie_samesite, is_local
from .schemas import UserCreate, UserRead, UserUpdate
from .service import create_user, delete_user, get_user_or_404, list_users, update_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/token")
async def get_token(
    request: Request,
    token: str | None = Depends(get_access_token),
    refresh_token: str | None = None,
    db: AsyncSession = Depends(get_async_db),
) -> JSONResponse:
    from ..core.database import supabase_client
    from ..core.verfiy_token import verify_token_from_db

    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")
    
    if token:
        try:
            await verify_token_from_db(token, db)

            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                expires_in = max(0, int(payload.get("exp", 0)) - time.time())
            except Exception:
                expires_in = 3600
            
            is_local_request = is_local(request)
            token_response = {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": expires_in,
            }

            if is_local_request:
                token_response["refresh_token"] = refresh_token
            
            response = JSONResponse(content=token_response)
            response.headers["X-skip-camelize"] = "1"
            return response        
        except Exception:
            logger.info("Invalid token")
    
    if refresh_token:
        try:
            response = await supabase_client.auth.refresh_session(refresh_token)
            session = response.session
            if session and session.access_token:
                is_local_request = is_local(request)
                token_response = {
                    "access_token": session.access_token,
                    "token_type": "bearer",
                    "expires_in": session.expires_in,
                }

                if is_local_request:
                    token_response["refresh_token"] = refresh_token
                
                response = JSONResponse(content=token_response)

                samesite = get_cookie_samesite(request, is_local_request)
                response.set_cookie(
                    key="refresh_token",
                    value=session.refresh_token,
                    httponly=True,
                    max_age=30 * 24 * 3600,
                    samesite=samesite,
                    secure=(samesite == "none") or (not is_local_request),
                )
                response.headers["X-skip-camelize"] = "1"
                return response        
        except Exception as refresh_error:
            logger.error("Error refreshing token", exc_info=refresh_error)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})



@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_route(
    payload: UserCreate,
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    """Create a new user."""

    user = await create_user(db, payload)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def list_users_route(
    include_deleted: bool = Query(default=False),
    db: AsyncSession = Depends(get_async_db),
) -> list[UserRead]:
    """List users with optional deleted rows."""

    users = await list_users(db, include_deleted=include_deleted)
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_uuid}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_route(
    user_uuid: str,
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    """Read a single active user by UUID."""

    user = await get_user_or_404(db, user_uuid)
    return UserRead.model_validate(user)


@router.patch("/{user_uuid}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user_route(
    user_uuid: str,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    """Partially update an active user."""

    user = await update_user(db, user_uuid, payload)
    return UserRead.model_validate(user)


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    user_uuid: str,
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """Soft-delete a user by UUID."""

    await delete_user(db, user_uuid)
