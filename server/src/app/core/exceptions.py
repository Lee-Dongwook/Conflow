from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class DatabaseConnectionError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    
    error_response: dict[str, Any] = {
        "success": False,
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
    }

    if isinstance(exc, DatabaseConnectionError):
        return JSONResponse(status_code=503, content=error_response)

    return JSONResponse(status_code=500, content=error_response)
