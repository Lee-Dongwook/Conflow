"""In-memory vector store for local development and tests."""

import math

from rag.schemas import DocumentChunk, QueryResult
from rag.stores.base import VectorStore


class InMemoryVectorStore(VectorStore):
    """Dict-backed store with cosine similarity."""

    def __init__(self) -> None:
        """Initialize empty store."""
        self._store: dict[str, DocumentChunk] = {}

    def add_documents(self, chunks: list[DocumentChunk]) -> None:
        """Add chunks; each must include an embedding."""
        for chunk in chunks:
            if chunk.embedding is None:
                msg = f"DocumentChunk {chunk.id} has no embedding."
                raise ValueError(msg)
            self._store[chunk.id] = chunk

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[QueryResult]:
        """Rank all stored chunks by cosine similarity."""
        if not self._store:
            return []

        scored = [
            (self._cosine_similarity(query_embedding, chunk.embedding or []), chunk)
            for chunk in self._store.values()
            if chunk.embedding
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)

        return [
            QueryResult(chunk=chunk, score=score)
            for score, chunk in scored[:top_k]
        ]

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Cosine similarity in [0, 1] when vectors are non-zero."""
        if not vec1 or not vec2:
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2, strict=True))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot / (norm1 * norm2)
