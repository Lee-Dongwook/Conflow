import logging
import secrets
from typing import TypedDict

from fastapi import HTTPException
from starlette.requests import Request

class AuthInfo(TypedDict):
    """Authentication information."""

    access_token: str
    refresh_token: str
    expires_in: int

logger = logging.getLogger(__name__)

async def get_auth_info(request: Request) -> AuthInfo:
    """Get authentication information from the request."""
