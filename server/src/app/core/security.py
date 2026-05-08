from __future__ import annotations

import hashlib
import hmac
import os

from cryptography.fernet import Fernet

_fernet: Fernet | None = None
_context_fernet: Fernet | None = None
_context_fernet_initialized: bool = False
_signing_key: bytes | None = None

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

def encrypt_value(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Value must be a string")
    fernet = _get_fernet()
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(en_value: str) -> str:
    if not isinstance(en_value, str):
        raise TypeError("Value must be a string")
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

# ----
# Context Token (X-Context-Token)
# TODO: Later
# ----


