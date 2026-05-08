"""ASGI entrypoint for the Conflow API."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.home.api import router as home_router
from src.app.user.api import router as user_router


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

_cors_raw = os.environ.get("CORS_ORIGIN", "")
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(home_router)
app.include_router(user_router)


def main() -> None:
    """Run the development server with auto-reload."""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
