"""HTTP routes for the home API surface."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    """Return a minimal liveness response for load balancers and probes."""
    return JSONResponse(
        content={"MESSAGE": "OK"},
        headers={"X-skip-camelize": "1"},
    )
