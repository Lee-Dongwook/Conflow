"""
This module provides Google OAuth authentication API endpoints.
"""

import logging
import os
from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from starlette.config import Config

logger = logging.getLogger(__name__)

router = APIRouter()

# Use environ mapping so values loaded by shared_init/dotenv are picked up
config = Config(environ=os.environ)

# Initialize OAuth
oauth = OAuth(config)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")

_oauth_registered = False


def _ensure_oauth_registered() -> None:
    global _oauth_registered
    if _oauth_registered:
        return
    if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured.",
        )
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
    _oauth_registered = True


@router.get("/google/login")
async def google_login(request: Request) -> RedirectResponse:
    _ensure_oauth_registered()
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request) -> dict[str, Any]:
    _ensure_oauth_registered()
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to obtain access token: {e}"
        )

    user_info = await oauth.google.parse_id_token(token)

    return {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "sub": user_info.get("sub"),
    }
