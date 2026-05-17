import math

from rag.schemas import DocumentChunk, QueryResult


class VectorStore:
    """
    A basic in-memory vector store for demonstration purposes.
    In a production environment, this would be replaced by a dedicated vector database.
    """

    def __init__(self):
        """
        Initializes the in-memory vector store.
        """
        self.store: dict[str, DocumentChunk] = {}

    def add_documents(self, chunks: list[DocumentChunk]):
        """
        Adds a list of document chunks to the vector store.

        Args:
            chunks: A list of DocumentChunk objects to add.
        """
        for chunk in chunks:
            if chunk.embedding is None:
                raise ValueError(f"DocumentChunk {chunk.id} has no embedding.")
            self.store[chunk.id] = chunk
        print(f"Added {len(chunks)} document chunks to the store.")

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[QueryResult]:
        """
        Searches the vector store for the most similar document chunks to the query embedding.

        Args:
            query_embedding: The embedding of the query.
            top_k: The number of top similar results to return.

        Returns:
            A list of QueryResult objects, sorted by similarity score in descending order.
        """
        if not self.store:
            return []

        # Calculate cosine similarity for all stored chunks
        similarities: list[tuple[float, DocumentChunk]] = []
        for chunk in self.store.values():
            if chunk.embedding:
                score = self._cosine_similarity(query_embedding, chunk.embedding)
                similarities.append((score, chunk))

        # Sort by similarity and return top_k results
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results: list[QueryResult] = []
        for score, chunk in similarities[:top_k]:
            results.append(QueryResult(chunk=chunk, score=score))
        
        return results

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        Calculates the cosine similarity between two vectors.

        Args:
            vec1: The first vector.
            vec2: The second vector.

        Returns:
            The cosine similarity score.
        """
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        magnitude_v1 = math.sqrt(sum(v1 * v1 for v1 in vec1))
        magnitude_v2 = math.sqrt(sum(v2 * v2 for v2 in vec2))

        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0

        return dot_product / (magnitude_v1 * magnitude_v2)
