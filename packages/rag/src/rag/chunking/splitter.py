"""Document text splitting."""

import uuid
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import RagSettings
from rag.schemas import DocumentChunk


class TextChunker:
    """Splits raw text into ``DocumentChunk`` instances."""

    def __init__(self, settings: RagSettings | None = None) -> None:
        """Build splitter from chunk size / overlap in settings."""
        resolved = settings or RagSettings()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=resolved.chunk_size,
            chunk_overlap=resolved.chunk_overlap,
        )

    def chunk_text(
        self,
        text_content: str,
        source_metadata: dict[str, Any],
    ) -> list[DocumentChunk]:
        """Split text and attach metadata to each chunk."""
        segments = self._splitter.split_text(text_content)
        return [
            DocumentChunk(
                id=str(uuid.uuid4()),
                text_content=segment.strip(),
                metadata={
                    "chunk_idx": index,
                    "length": len(segment),
                    **source_metadata,
                },
            )
            for index, segment in enumerate(segments)
            if segment.strip()
        ]
