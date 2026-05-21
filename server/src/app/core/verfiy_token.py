import os
import time

import jwt
from cachetools import TTLCache
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2AuthorizationCodeBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.schemas import UserRead
from ..user.service import get_user_by_supabase_uuid, get_user_by_uuid
from . import logger
from .database import get_async_db
from .security import parse_execution_token

bearer_scheme = HTTPBearer(auto_error=False)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",
    tokenUrl="",
    scopes={},
)
oauth2_scheme.auto_error = False

_READ_CACHE_METHODS = frozenset(["GET", "HEAD", "OPTIONS"])
_VERIFY_TOKEN_READ_CACHE_TTL = max(0, int(os.environ.get("VERIFY_TOKEN_READ_CACHE_TTL", "180")))
_VERIFY_TOKEN_CACHE_MAXSIZE = max(0, int(os.environ.get("VERIFY_TOKEN_CACHE_MAXSIZE", "1024")))

_verfiy_token_cache: TTLCache[str, UserRead] | None = (
    TTLCache(maxsize=_VERIFY_TOKEN_CACHE_MAXSIZE, ttl=_VERIFY_TOKEN_READ_CACHE_TTL)
    if _VERIFY_TOKEN_READ_CACHE_TTL > 0
    else None
)

async def get_access_token(
    oauth2_token: str | None = Depends(oauth2_scheme),
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if oauth2_token:
        return oauth2_token
    if bearer:
        return bearer.credentials
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def verify_token_from_db(token: str, db: AsyncSession) -> UserRead:
    if token.startswith("lbe."):
        parsed = parse_execution_token(token)
        if parsed is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid execution token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_uuid, _ = parsed
        user = await get_user_by_uuid(user_uuid, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserRead(
            uuid=user.uuid,
            name=user.name,
            email=user.email,
            profile_image_url=user.profile_image_url,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    try:
        from .database import supabase_client

        supabase_user_response = await supabase_client.auth.get_user(token)
        supabase_user = supabase_user_response.user

        if supabase_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        detail = "Invalid token"
        if "expired" in str(e).lower():
            detail = "Token expired"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    
    user = await get_user_by_supabase_uuid(supabase_user.id, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserRead(
        uuid=user.uuid,
        name=user.name,
        email=user.email,
        profile_image_url=user.profile_image_url,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

async def set_cached_verified_user(cache: TTLCache[str, UserRead], token: str, user: UserRead) -> None:  # noqa: E501
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        if exp is not None and float(exp) - time.time() < _VERIFY_TOKEN_READ_CACHE_TTL:
            return
    except Exception as exc:
        logger.debug("Failed to decode token", exc_info=exc)
    cache[token] = user


async def verify_token(
    request: Request,
    token: str = Depends(get_access_token),
    db: AsyncSession = Depends(get_async_db),
) -> UserRead:
    cache = _verfiy_token_cache
    use_read_cache = cache is not None and request.method in _READ_CACHE_METHODS and not token.startswith("lbe.")  # noqa: E501

    user: UserRead | None = cache.get(token) if use_read_cache else None

    if user is None:
        user = await verify_token_from_db(token, db)
        if use_read_cache:
            await set_cached_verified_user(cache, token, user)
    else:
        logger.debug("Token verified from cache", extra={"token": token})

    request.state.user = {
        "uuid": str(user.uuid),
        "email": user.email,
        "name": user.name,
    }

    return user
