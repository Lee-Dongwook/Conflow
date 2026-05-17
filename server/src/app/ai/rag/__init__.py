"""
Server RAG facade — re-exports from the ``vector-rag`` workspace package.

Use ``from src.app.ai.rag import ...`` in FastAPI routes, or import ``rag`` directly.
"""

from rag import (
    DocumentChunk,
    QueryResult,
    RAGQuery,
    RAGService,
    RagSettings,
    create_rag_service,
    get_settings,
)
from rag.embeddings import EmbeddingProvider, OpenAIEmbeddingProvider
from rag.processing import DocumentProcessor
from rag.stores import InMemoryVectorStore, PgVectorStore, VectorStore

# Backward-compatible alias for the old server stub name.
EmbeddingModel = OpenAIEmbeddingProvider

__all__ = [
    "DocumentChunk",
    "DocumentProcessor",
    "EmbeddingModel",
    "EmbeddingProvider",
    "InMemoryVectorStore",
    "OpenAIEmbeddingProvider",
    "PgVectorStore",
    "QueryResult",
    "RAGQuery",
    "RAGService",
    "RagSettings",
    "VectorStore",
    "create_rag_service",
    "get_settings",
]
