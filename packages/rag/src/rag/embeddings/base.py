"""Embedding provider protocol."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Converts text into dense vectors."""

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string."""
        ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple strings."""
        ...
