"""Load files and produce chunks."""

from pathlib import Path
from typing import Any

from rag.chunking.splitter import TextChunker
from rag.config import RagSettings
from rag.schemas import DocumentChunk


class DocumentProcessor:
    """Loads plain-text files and splits them into chunks."""

    def __init__(
        self,
        chunker: TextChunker | None = None,
        settings: RagSettings | None = None,
    ) -> None:
        """Inject chunker or build from settings."""
        resolved = settings or RagSettings()
        self._chunker = chunker or TextChunker(resolved)

    def load_document(self, file_path: str) -> str:
        """Read UTF-8 text from disk."""
        path = Path(file_path)
        if not path.is_file():
            msg = f"Document not found at {file_path}"
            raise FileNotFoundError(msg)
        return path.read_text(encoding="utf-8")

    def chunk_document(
        self,
        text_content: str,
        source_metadata: dict[str, Any],
    ) -> list[DocumentChunk]:
        """Split loaded text into chunks."""
        return self._chunker.chunk_text(text_content, source_metadata)
