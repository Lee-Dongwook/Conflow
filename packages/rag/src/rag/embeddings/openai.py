"""OpenAI embeddings via LangChain."""

import os

from langchain_openai import OpenAIEmbeddings

from rag.config import RagSettings


class OpenAIEmbeddingProvider:
    """LangChain-backed OpenAI embedding client."""

    def __init__(self, settings: RagSettings | None = None) -> None:
        """Initialize with settings; resolves API key from RAG_ or OPENAI_ env."""
        resolved = settings or RagSettings()
        api_key = resolved.openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            msg = "Set RAG_OPENAI_API_KEY or OPENAI_API_KEY for OpenAIEmbeddingProvider."
            raise ValueError(msg)
        self._client = OpenAIEmbeddings(
            model=resolved.openai_embedding_model,
            api_key=api_key,
        )

    def embed_text(self, text: str) -> list[float]:
        """Return embedding for one text."""
        return self._client.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for many texts."""
        return self._client.embed_documents(texts)
