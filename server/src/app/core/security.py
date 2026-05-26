from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, cast

import jwt
from cryptography.fernet import Fernet
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator
from typing_extensions import override

from .config import get_settings

_fernet: Fernet | None = None
_context_fernet: Fernet | None = None
_context_fernet_initialized: bool = False
_signing_key: bytes | None = None

_CONTEXT_TOKEN_ALGORITHM = "HS256"  # noqa: S105
_CONTEXT_TOKEN_TTL = 3600  # 1 hour
_CONTEXT_REFRESH_THRESHOLD = 900  # 15 minutes
_EXECUTION_TOKEN_TTL = 300  # 5 minutes
_SERVICE_ACCESS_TOKEN_ALGORITHM = "HS256"  # noqa: S105
SERVICE_TOKEN_PREFIX = "conf."  # noqa: S105
_SENSITIVE_KEY_PATTERNS: frozenset[str] = frozenset(
    {"secret", "key", "token", "password", "credential", "auth", "bearer", "private"}
)

def _get_signing_key() -> bytes:
    global _signing_key
    if _signing_key is None:
        SIGNING_KEY = os.environ.get("SIGNING_KEY", "")
        if not SIGNING_KEY:
            raise ValueError("SIGNING_KEY is not set")
        _signing_key = SIGNING_KEY.encode()
    return _signing_key

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        ENCRYPTION_KEY = os.environ.get("SECRET_ENCRYPTION_KEY") 
        if not ENCRYPTION_KEY:
            raise ValueError("SECRET_ENCRYPTION_KEY is not set")
        try:
            _fernet = Fernet(ENCRYPTION_KEY.encode())
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid SECRET_ENCRYPTION_KEY: {e}") from e
    return _fernet

def _get_context_fernet() -> Fernet | None:
    global _context_fernet, _context_fernet_initialized
    if not _context_fernet_initialized:
        key = get_settings().CONTEXT_COOKIE_KEY
        if key:
            try:
                _context_fernet = Fernet(key.encode())
            except (ValueError, TypeError) as e:
                raise ValueError("Invalid CONTEXT_COOKIE_KEY") from e
        _context_fernet_initialized = True
    return _context_fernet

def encrypt_value(value: str) -> str:
    fernet = _get_fernet()
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(en_value: str) -> str:
    fernet = _get_fernet()
    try:
        return fernet.decrypt(en_value.encode()).decode()
    except Exception as e:
        raise ValueError(f"Invalid encrypted value: {e}") from e
    

def create_signature(message: str) -> str:
    key = _get_signing_key()
    return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()

def verify_signature(message: str, signature: str) -> bool:
    key = _get_signing_key()
    expected_signature = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

def generate_context_token(user_uuid: str, payload: dict[str, Any]) -> str:
    signing_key = _get_signing_key()
    now = int(time.time())

    full_payload = {"sub": user_uuid, "iat": now, "exp": now + _CONTEXT_TOKEN_TTL, **payload}
    return jwt.encode(full_payload, signing_key, algorithm=_CONTEXT_TOKEN_ALGORITHM)

def verify_context_token(token: str) -> dict[str, Any] | None:
    signing_key = _get_signing_key()
    try:
        return cast("dict[str, Any]", jwt.decode(token, signing_key, algorithms=[_CONTEXT_TOKEN_ALGORITHM]))  # noqa: E501
    except (jwt.PyJWTError, ValueError):
        return None

def encrypt_context_cookie(payload: dict[str, Any]) -> str:
    fernet = _get_context_fernet()
    if fernet is not None and get_settings().ENCRYPT_CONTEXT_COOKIE:
        data = json.dumps(payload).encode()
        return f"v1:{fernet.encrypt(data).decode()}"
    user_uuid = payload.get("sub", "")
    return generate_context_token(user_uuid, {k: v for k, v in payload.items() if k != "sub"})

def decrypt_context_cookie(token: str) -> dict[str, Any] | None:
    if token.startswith("v1:"):
        fernet = _get_context_fernet()
        if fernet is None:
            return None
        try:
            encrypted = token.removeprefix("v1:")
            return cast("dict[str, Any]", json.loads(fernet.decrypt(encrypted.encode()).decode()))
        except Exception:
            return None
    
    return verify_context_token(token)

def should_refresh_context_token(payload: dict[str, Any]) -> bool:
    exp = payload.get("exp")
    if not exp:
        return False
    
    remaining = int(exp) - int(time.time())
    return remaining < _CONTEXT_REFRESH_THRESHOLD

def generate_execution_token(user_uuid: str, execution_uuid: str) -> str:
    expires_at = int(time.time()) + _EXECUTION_TOKEN_TTL
    message = f"{user_uuid}:{execution_uuid}:{expires_at}"
    sig = create_signature(message)
    b64 = base64.urlsafe_b64encode(message.encode()).decode().rstrip("=")
    return f"conf.{b64}.{sig}"

def parse_execution_token(token: str) -> tuple[str, str] | None:
    if not token.startswith("conf."):
        return None
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        _, b64, sig = parts
        padded = b64 + "=" * (-len(b64) % 4)
        message = base64.urlsafe_b64decode(padded).decode()
        if not verify_signature(message, sig):
            return None
        user_uuid, execution_uuid, exp_str = message.split(":")
        if int(exp_str) < int(time.time()):
            return None
        return user_uuid, execution_uuid
    except Exception:
        return None

def generate_service_access_token(
    user_uuid: str,
    client_id: str,
    scopes: list[str] | None = None,
    credential_id: str | None = None,
    user_metadata: dict[str, Any] | None = None,
) -> tuple[str, int]:
    ttl = max(60, int(os.environ.get("AUTH_ACCESS_TOKEN_TTL", "3600")))
    now = int(time.time())
    payload: dict[str, Any] = {
        "iss": os.environ.get("AUTH_TOKEN_ISSUER", os.environ.get("MCP_TOKEN_ISSUER", "conflow-auth")),  # noqa: E501
        "aud": os.environ.get("AUTH_TOKEN_AUDIENCE", os.environ.get("MCP_TOKEN_AUDIENCE", "conflow-api")),  # noqa: E501
        "sub": client_id,
        "client_id": client_id,
        "user_uuid": user_uuid,
        "scopes": scopes or [],
        "iat": now,
        "exp": now + ttl,
    }

    if credential_id:
        payload["credential_id"] = credential_id
    if user_metadata:
        payload["user_metadata"] = user_metadata
    
    token = jwt.encode(payload, _get_signing_key(), algorithm=_SERVICE_ACCESS_TOKEN_ALGORITHM)
    return f"{SERVICE_TOKEN_PREFIX}{token}", ttl

def parse_service_access_token(token: str) -> dict[str, Any] | None:
    if not token.startswith(SERVICE_TOKEN_PREFIX):
        return None

    raw_token = token.removeprefix(SERVICE_TOKEN_PREFIX)
    issuer = os.environ.get("AUTH_TOKEN_ISSUER", os.environ.get("MCP_TOKEN_ISSUER", "conflow-auth"))
    audience = os.environ.get("AUTH_TOKEN_AUDIENCE", os.environ.get("MCP_TOKEN_AUDIENCE", "conflow-api"))  # noqa: E501
    try:
        return cast(
            "dict[str, Any]",
            jwt.decode(
                raw_token,
                _get_signing_key(),
                algorithms=[_SERVICE_ACCESS_TOKEN_ALGORITHM],
                issuer=issuer,
                audience=audience,
            )
        )
    except (jwt.PyJWTError, ValueError):
        return None

class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    @override
    def process_bind_param(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return value
        return encrypt_value(value)
    
    @override
    def process_result_value(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return value
        try:
            return decrypt_value(value)
        except ValueError:
            return value

def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-","").replace("_","")
    return any(pattern in normalized for pattern in _SENSITIVE_KEY_PATTERNS)

def encrypt_sensitive_dict_values(d: dict[str, Any]| None) -> dict[str, Any]| None:
    if d is None:
        return None
    return {k: (encrypt_value(v) if isinstance(v, str) and _is_sensitive_key(k) else v) for k, v in d.items()}  # noqa: E501

def decrypt_sensitive_dict_values(d: dict[str, Any]| None) -> dict[str, Any]| None:
    if d is None:
        return None
    result: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str) and _is_sensitive_key(k):
            try:
                result[k] = decrypt_value(v)
            except ValueError:
                result[k] = v
        else:
            result[k] = v
    return result
