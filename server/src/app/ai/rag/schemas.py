from typing import Any

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """
    Represents a chunk of a document, including its content, metadata, and vector embedding.
    """
    id: str = Field(..., description="Unique identifier for the document chunk.")
    text_content: str = Field(..., description="The textual content of the chunk.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata associated with the chunk.")  # noqa: E501
    embedding: list[float] | None = Field(None, description="Vector embedding of the text content.")

class QueryResult(BaseModel):
    """
    Represents a result obtained from a RAG query, including the retrieved chunk and its relevance score.
    """  # noqa: E501
    chunk: DocumentChunk = Field(..., description="The retrieved document chunk.")
    score: float = Field(..., description="Relevance score of the chunk to the query.")

class RAGQuery(BaseModel):
    """
    Represents a query to the RAG system.
    """
    query_text: str = Field(..., description="The natural language query text.")
    top_k: int = Field(5, description="The number of top relevant document chunks to retrieve.")

