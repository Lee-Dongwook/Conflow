import logging
import os
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def is_allowed_origin(origin: str) -> bool:
    if not origin:
        return False

    cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    allowed_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]

    if origin in allowed_origins or "*" in allowed_origins:
        return True

    cors_origins_regex = os.environ.get("CORS_ALLOWED_ORIGINS_REGEX")
    if cors_origins_regex:
        try:
            if re.fullmatch(cors_origins_regex, origin):
                return True
        except re.error as e:
            logger.error(f"Invalid CORS allowed origins regex: {e}")
            return False

    return False

def is_allowed_redirect_uri(uri: str) -> bool:
    if not uri:
        return False

    try:
        parsed = urlparse(uri)
        origin = f"{parsed.scheme}://{parsed.netloc}"

        if parsed.hostname in ["localhost", "127.0.0.1"] or (parsed.hostname and parsed.hostname.startswith("192.168.")):  # noqa: E501
            return True
        
        return is_allowed_origin(origin)
    except Exception:
        return False
