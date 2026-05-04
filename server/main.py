"""ASGI entrypoint for the Conflow API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.app.home.api import router as home_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    yield


app = FastAPI(
    title="Conflow API",
    description="Conflow API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(home_router)


def main() -> None:
    """Run the development server with auto-reload."""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
