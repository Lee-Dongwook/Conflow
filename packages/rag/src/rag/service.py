"""RAG orchestration — index, retrieve, generate (stub)."""

import logging
from typing import Any, Literal

from rag.cache.base import CacheBackend
from rag.cache.noop import NoOpCache
from rag.config import RagSettings, get_settings
from rag.embeddings.base import EmbeddingProvider
from rag.embeddings.openai import OpenAIEmbeddingProvider
from rag.processing.document_processor import DocumentProcessor
from rag.schemas import DocumentChunk, QueryResult, RAGQuery
from rag.stores.base import VectorStore
from rag.stores.memory import InMemoryVectorStore
from rag.stores.pgvector import PgVectorStore

logger = logging.getLogger(__name__)

StoreKind = Literal["memory", "pgvector"]


class RAGService:
    """Coordinates document processing, embeddings, and vector search."""

    def __init__(
        self,
        document_processor: DocumentProcessor,
        embedding_model: EmbeddingProvider,
        vector_store: VectorStore,
        cache: CacheBackend | None = None,
    ) -> None:
        """Wire dependencies explicitly (no hidden globals)."""
        self.document_processor = document_processor
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.cache = cache or NoOpCache()

    def index_document(
        self,
        file_path: str,
        source_metadata: dict[str, Any],
    ) -> list[DocumentChunk]:
        """Load, chunk, embed, and persist a document."""
        logger.info("Indexing document: %s", file_path)
        text_content = self.document_processor.load_document(file_path)
        chunks = self.document_processor.chunk_document(text_content, source_metadata)

        texts = [chunk.text_content for chunk in chunks]
        embeddings = self.embedding_model.embed_documents(texts)
        embedded = [
            chunk.model_copy(update={"embedding": vector})
            for chunk, vector in zip(chunks, embeddings, strict=True)
        ]

        self.vector_store.add_documents(embedded)
        logger.info("Indexed %s chunks from %s", len(embedded), file_path)
        return embedded

    def retrieve(self, query: RAGQuery) -> list[QueryResult]:
        """Embed query text and search the vector store."""
        logger.info("Retrieving for query: %s", query.query_text)
        query_embedding = self.embedding_model.embed_text(query.query_text)
        results = self.vector_store.search(query_embedding, query.top_k)
        logger.info("Retrieved %s results", len(results))
        return results

    def generate_response(self, query: RAGQuery) -> str:
        """Placeholder generation — concatenate retrieved context."""
        retrieved = self.retrieve(query)
        if not retrieved:
            return "Relevant information could not be found."

        context = "\n\n".join(
            f"Source: {item.chunk.metadata.get('file_path', 'N/A')}\n{item.chunk.text_content}"
            for item in retrieved
        )
        return (
            f"Based on the following retrieved information:\n\n{context}\n\n"
            f"LLM response for: '{query.query_text}' (not wired yet)."
        )


def create_rag_service(
    *,
    store: StoreKind = "memory",
    settings: RagSettings | None = None,
    cache: CacheBackend | None = None,
) -> RAGService:
    """
    Factory for local development.

    Args:
        store: ``memory`` (default) or ``pgvector``.
        settings: Override env-based settings.
        cache: Optional cache backend (defaults to no-op).
    """
    resolved = settings or get_settings()
    vector_store: VectorStore = (
        PgVectorStore(resolved) if store == "pgvector" else InMemoryVectorStore()
    )
    return RAGService(
        document_processor=DocumentProcessor(settings=resolved),
        embedding_model=OpenAIEmbeddingProvider(resolved),
        vector_store=vector_store,
        cache=cache,
    )
