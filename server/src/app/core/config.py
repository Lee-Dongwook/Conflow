from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings): 
    # Operational policy file selector. Resolves to config/{SYSTEM_POLICY}.toml
    SYSTEM_POLICY: str = "default"

    # Fernet key for context cookie encryption (URL-safe base64-encoded 32-byte key).
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # noqa: E501
    # If unset, context cookies fall back to JWT signing regardless of ENCRYPT_CONTEXT_COOKIE.
    CONTEXT_COOKIE_KEY: str | None = None

    # Encrypt context cookie with Fernet when CONTEXT_COOKIE_KEY is set.
    # Set to False to force JWT signing even if CONTEXT_COOKIE_KEY is present.
    ENCRYPT_CONTEXT_COOKIE: bool = True

    model_config = SettingsConfigDict(
        env_file=None, # Disable direct file reading to avoid conflict with shared_init.load_dotenv
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
