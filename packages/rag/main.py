from fastapi import FastAPI, APIRouter, HTTPException
from typing import Literal, Any, List
from rag.config import RagSettings, get_settings
from rag.schemas import DocumentChunk, QueryResult, RAGQuery
from rag.service import RAGService, create_rag_service, StoreKind
from rag.cache.base import CacheBackend
from rag.cache.noop import NoOpCache

# Initialize FastAPI app
app = FastAPI(
    title="RAG Service",
    description="Vector RAG microservice for document indexing and retrieval",
    version="0.1.0",
)

# --- Configuration and Service Initialization ---
# This part assumes synchronous initialization for simplicity.
# For more complex setups, consider async initialization or dependency injection.
_settings: RagSettings = get_settings()
_cache_backend: CacheBackend = NoOpCache() # Or your preferred cache backend
_rag_service_instance: RAGService

@app.on_event("startup")
async def startup_event():
    global _rag_service_instance
    # Using 'pgvector' as default for containerized environment,
    # can be configured via environment variables or settings.
    _rag_service_instance = create_rag_service(
        store="pgvector",
        settings=_settings,
        cache=_cache_backend
    )
    print("RAGService initialized with PgVectorStore.")

# --- API Endpoints ---
rag_router = APIRouter(prefix="/rag", tags=["RAG Operations"])

@rag_router.post("/index", response_model=List[DocumentChunk])
async def index_document_endpoint(
    file_path: str,
    source_metadata: dict[str, Any]
) -> List[DocumentChunk]:
    """
    Indexes a document by loading, chunking, embedding, and persisting it.
    """
    try:
        return _rag_service_instance.index_document(file_path, source_metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {e}")

@rag_router.post("/retrieve", response_model=List[QueryResult])
async def retrieve_endpoint(query: RAGQuery) -> List[QueryResult]:
    """
    Embeds query text and searches the vector store.
    """
    try:
        return _rag_service_instance.retrieve(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {e}")

@rag_router.post("/generate", response_model=str)
async def generate_response_endpoint(query: RAGQuery) -> str:
    """
    Generates a response based on retrieved context.
    """
    try:
        return _rag_service_instance.generate_response(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {e}")

app.include_router(rag_router)

# Example for local testing (not typically used in production Docker setup)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
