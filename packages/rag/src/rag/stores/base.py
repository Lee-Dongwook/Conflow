"""Vector store protocol."""

from abc import ABC, abstractmethod

from rag.schemas import DocumentChunk, QueryResult


class VectorStore(ABC):
    """Persists chunks and runs similarity search."""

    @abstractmethod
    def add_documents(self, chunks: list[DocumentChunk]) -> None:
        """Upsert chunks that already carry embeddings."""
        ...

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[QueryResult]:
        """Return top-k chunks by similarity to the query vector."""
        ...
