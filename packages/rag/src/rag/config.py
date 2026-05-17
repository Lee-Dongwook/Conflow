"""Environment-backed configuration for the RAG package."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RagSettings(BaseSettings):
    """Settings loaded from environment variables (prefix ``RAG_``)."""

    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/conflow",
        description="SQLAlchemy URL for pgvector storage.",
    )
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key; falls back to OPENAI_API_KEY when unset.",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model name.",
    )
    embedding_dimensions: int = Field(
        default=1536,
        description="Expected embedding vector size (must match model).",
    )
    chunk_size: int = Field(default=1000, ge=1)
    chunk_overlap: int = Field(default=200, ge=0)
    default_top_k: int = Field(default=5, ge=1)
    # redis_url: str | None = None  # optional cache — wire when redis extra is used


@lru_cache
def get_settings() -> RagSettings:
    """Return cached settings instance."""
    return RagSettings()
