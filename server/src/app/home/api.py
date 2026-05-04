"""HTTP routes for the home API surface."""

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Return a minimal liveness response for load balancers and probes."""
    return {"MESSAGE": "OK"}
