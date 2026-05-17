"""Pydantic models shared across indexing and retrieval."""

from typing import Any

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """A text chunk with optional metadata and embedding."""

    id: str = Field(..., description="Unique identifier for the chunk.")
    text_content: str = Field(..., description="Chunk body text.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata (source id, page, etc.).",
    )
    embedding: list[float] | None = Field(
        default=None,
        description="Vector embedding; required before persistence.",
    )


class QueryResult(BaseModel):
    """A retrieved chunk with similarity score."""

    chunk: DocumentChunk
    score: float = Field(..., ge=0.0, le=1.0)


class RAGQuery(BaseModel):
    """Natural-language retrieval request."""

    query_text: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1)
