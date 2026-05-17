"""Tests for in-memory vector store."""

from src.rag.schemas import DocumentChunk, RAGQuery
from src.rag.service import RAGService
from src.rag.stores.memory import InMemoryVectorStore


class _StubEmbeddings:
    """Deterministic embeddings for tests."""

    def embed_text(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0] if "query" in text.lower() else [0.9, 0.1, 0.0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]


class _StubProcessor:
    """Returns fixed chunks without touching disk."""

    def load_document(self, file_path: str) -> str:
        return f"content from {file_path}"

    def chunk_document(self, text_content: str, source_metadata: dict) -> list[DocumentChunk]:
        return [
            DocumentChunk(
                id="chunk-1",
                text_content=text_content,
                metadata=source_metadata,
            ),
        ]


def test_retrieve_returns_scored_chunk() -> None:
    """Indexed chunk should be retrievable with a positive score."""
    store = InMemoryVectorStore()
    service = RAGService(
        document_processor=_StubProcessor(),  # type: ignore[arg-type]
        embedding_model=_StubEmbeddings(),  # type: ignore[arg-type]
        vector_store=store,
    )
    chunks = service.index_document("/tmp/doc.txt", {"file_path": "/tmp/doc.txt"})
    assert len(chunks) == 1
    assert chunks[0].embedding is not None

    results = service.retrieve(RAGQuery(query_text="my query", top_k=1))
    assert len(results) == 1
    assert results[0].chunk.id == "chunk-1"
    assert results[0].score > 0.0
