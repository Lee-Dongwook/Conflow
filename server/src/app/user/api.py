"""HTTP routes for user CRUD operations."""
import base64
import hmac
import json
import logging
import os
import time
from functools import lru_cache
from typing import Any
from urllib.parse import unquote

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.security import generate_service_access_token
from ..core.utils import is_allowed_redirect_uri
from ..core.verfiy_token import get_access_token
from ..user.utils import get_user_by_uuid
from .lib import get_cookie_samesite, is_local
from .schemas import TokenRefresh, UserCreate, UserRead, UserUpdate
from .service import create_user, delete_user, get_user_or_404, list_users, update_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])
ClientCredentialConifg = dict[str, Any]
_DUMMY_CLIENT_SECRET = 'conflow-client-secret-sample'

def _load_client_credentials() -> dict[str, ClientCredentialConifg]:
    raw_credentials = os.environ.get("AUTH_CLIENT_CREDENTIALS") or os.environ.get("MCP_CLIENT_CREDENTIALS")  # noqa: E501
    if not raw_credentials:
        return {}
    
    try:
        credentials = json.loads(raw_credentials)
    except Exception as e:
        logger.error(f"Error loading client credentials: {e}")
        return {}
    if not isinstance(credentials, dict):
        logger.error("Client credentials must be a dictionary")
        return {}
    return {str(key): value for key, value in credentials.items() if isinstance(value, dict)}

def _get_basic_client_credentials(request: Request) -> tuple[str, str] | None:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.lower().startswith("basic "):
        return None
    
    try:
        encoded_credentials = authorization.split(" ",1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials, validate=True).decode()
    except Exception:
        return None
    
    client_id, separator, client_secret = decoded_credentials.partition(":")
    if not separator:
        return None
    return unquote(client_id), unquote(client_secret)

async def _issue_client_credentials_token(
    request: Request,
    client_id: str | None,
    client_secret: str | None,
    scope: str | None,
    db: AsyncSession,
) -> JSONResponse:
    basic_credentials = _get_basic_client_credentials(request)
    if basic_credentials:
        if client_id and not hmac.compare_digest(client_id, basic_credentials[0]):
            logger.warning("Client ID mismatch", extra={"client_id": client_id, "basic_credentials": basic_credentials[0]})  # noqa: E501
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
                headers={"WWW-Autenticate": 'Basic realm="token"'},
            )
        client_id, client_secret = basic_credentials

        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id and client_secret are required."
            )
        credentials = _load_client_credentials()
        credential = credentials.get(client_id)
        expected_secret = credential.get("client_secret") if credential else None
        secret_matches = hmac.compare_digest(str(expected_secret or _DUMMY_CLIENT_SECRET), client_secret)  # noqa: E501
        if credential is None or not expected_secret or not secret_matches:
            logger.warning("Invalid client credentials", extra={"client_id": client_id, "expected_secret": expected_secret})  # noqa: E501
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
                headers={"WWW-Autenticate": 'Basic realm="token"'},
            )
        user_uuid = credential.get("user_uuid")
        if not user_uuid:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Client credential is missing user_uuid.",
            )
        user = await get_user_by_uuid(str(user_uuid), db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found for client credential.",
            )
        
        allowed_scopes = credential.get("scopes") or []
        if isinstance(allowed_scopes, str):
            allowed_scopes = allowed_scopes.split()
        requested_scopes = scope.split() if scope else list(allowed_scopes)
        if any(requested_scopes not in allowed_scopes for requested_scopes in requested_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid scope requested.",
            )

        access_token, expires_in = generate_service_access_token(
            user_uuid = str(user.uuid),
            client_id = client_id,
            scopes = requested_scopes,
            credential_id = credential.get("credential_id"),
            user_metadata = credential.get("user_metadata") if isinstance(credential.get("user_metadata"), dict) else None,  # noqa: E501
        )

        response = JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": expires_in,
                "scope": " ".join(requested_scopes),
            }
        )
        response.headers["X-skip-camelize"] = "1"
        return response


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
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})  # noqa: E501

@router.post("/refresh_token", summary="Refresh a token")
async def refresh_token(
    request: Request,
    payload: TokenRefresh | None = None,
) -> JSONResponse:
    try:
        from ..core.database import supabase_client

        refresh_token = payload.refresh_token if payload else None
        if not refresh_token:
            refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required",
            )
        
        response = await supabase_client.auth.refresh_session(refresh_token)
        session = response.session

        if not session or not session.access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )
        is_local_request = is_local(request)
        token_response = {
            "access_token": session.access_token,
            "token_type": "bearer",
            "expires_in": session.expires_in,
        }
        if is_local_request:
            token_response["refresh_token"] = session.refresh_token
        
        json_response = JSONResponse(content=token_response)
        samesite = get_cookie_samesite(request, is_local_request)
        json_response.set_cookie(
            key="refresh_token",
            value=session.refresh_token,
            httponly=True,
            max_age=30 * 24 * 3600,
            samesite=samesite,
            secure=(samesite == "none") or (not is_local_request),
        )
        json_response.headers["X-skip-camelize"] = "1"
        return json_response
    except Exception as refresh_error:
        logger.error("Error refreshing token", exc_info=refresh_error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token",
        )


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
