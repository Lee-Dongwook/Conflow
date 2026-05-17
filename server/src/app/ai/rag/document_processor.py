import os
import uuid
from typing import Any

from rag.schemas import DocumentChunk


class DocumentProcessor:
    """
    Handles loading and chunking of documents for the RAG system.
    """

    def __init__(self):
        """
        Initializes the DocumentProcessor.
        """
        pass

    def load_document(self, file_path: str) -> str:
        """
        Loads the content of a document from the given file path.
        For now, it simply reads the file as plain text.

        Args:
            file_path: The path to the document file.

        Returns:
            The content of the document as a string.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found at {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:  # noqa: UP015
            content = f.read()
        return content

    def chunk_document(self, text_content: str, source_metadata: dict[str, Any]) -> list[DocumentChunk]:  # noqa: E501
        """
        Chunks the given text content into smaller DocumentChunk objects.
        This is a basic implementation and can be extended with more sophisticated chunking strategies.

        Args:
            text_content: The full text content of the document.
            source_metadata: Metadata to associate with each chunk (e.g., file_path, title).

        Returns:
            A list of DocumentChunk objects.
        """  # noqa: E501
        # Simple chunking for now: splitting by double newline characters.
        # In a real system, this would involve more intelligent splitting (e.g., SentenceTransformer, RecursiveCharacterTextSplitter).  # noqa: E501
        chunks = text_content.split('\n\n')
        document_chunks: list[DocumentChunk] = []

        for i, chunk_text in enumerate(chunks):
            if chunk_text.strip():  # Only add non-empty chunks
                chunk_id = str(uuid.uuid4())
                metadata = {
                    "chunk_idx": i,
                    "length": len(chunk_text),
                    **source_metadata
                }
                document_chunks.append(
                    DocumentChunk(
                        id=chunk_id,
                        text_content=chunk_text.strip(),
                        metadata=metadata
                    )
                )
        return document_chunks
