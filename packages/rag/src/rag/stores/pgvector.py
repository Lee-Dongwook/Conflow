"""PostgreSQL + pgvector store (draft — schema bootstrap only)."""

import logging
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from rag.config import RagSettings
from rag.schemas import DocumentChunk, QueryResult
from rag.stores.base import VectorStore

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class ChunkRow(Base):
    """ORM model for document chunks."""

    __tablename__ = "rag_document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))


class PgVectorStore(VectorStore):
    """
    pgvector-backed store.

    Requires ``CREATE EXTENSION vector`` on the target database.
    Similarity search is not implemented in this draft — use InMemoryVectorStore for dev.
    """

    def __init__(self, settings: RagSettings | None = None) -> None:
        """Create engine and ensure tables exist."""
        resolved = settings or RagSettings()
        self._settings = resolved
        self._engine = create_engine(resolved.database_url, echo=False)
        Base.metadata.create_all(self._engine)
        logger.info("PgVectorStore initialized (tables ensured).")

    def add_documents(self, chunks: list[DocumentChunk]) -> None:
        """Persist chunks with embeddings."""
        rows = []
        for chunk in chunks:
            if chunk.embedding is None:
                msg = f"DocumentChunk {chunk.id} has no embedding."
                raise ValueError(msg)
            rows.append(
                ChunkRow(
                    id=chunk.id,
                    text_content=chunk.text_content,
                    metadata_=chunk.metadata,
                    embedding=chunk.embedding,
                ),
            )

        with Session(self._engine) as session:
            for row in rows:
                session.merge(row)
            session.commit()

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[QueryResult]:
        """
        Cosine-distance search via pgvector ``<=>`` operator.

        Raises:
            NotImplementedError: Until SQL is wired with the correct dimension index.
        """
        _ = query_embedding, top_k
        with Session(self._engine) as session:
            session.execute(select(ChunkRow).limit(0))
        msg = (
            "PgVectorStore.search is not implemented yet. "
            "Add ORDER BY embedding <=> :query and map rows to QueryResult."
        )
        raise NotImplementedError(msg)
