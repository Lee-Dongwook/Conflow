"""
This module provides Google OAuth authentication API endpoints.
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from starlette.config import Config

router = APIRouter()

# Load configuration from .env file
config = Config(".env")

# Initialize OAuth
oauth = OAuth(config)

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default=None)
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", default=None)
GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI", default="http://localhost:8000/api/v1/auth/google/callback")

if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise ValueError("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment variables.")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get("/google/login")
async def google_login(request: Request) -> RedirectResponse:
    """
    Redirects the user to Google's OAuth login page.

    :param request: The incoming request.
    :return: A RedirectResponse to Google's authorization URL.
    """
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request) -> dict[str, Any]:
    """
    Handles the callback from Google OAuth, exchanges the authorization code for tokens,
    and retrieves user information.

    :param request: The incoming request with authorization code.
    :return: A dictionary containing user information or an error.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to obtain access token: {e}"
        )

    user_info = await oauth.google.parse_id_token(token)

    # Here you would typically save the user info to your database
    # and create a session for the user.
    # For now, we just return the user info.
    return {"user_info": user_info, "token": token}
