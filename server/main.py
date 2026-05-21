"""ASGI entrypoint for the Conflow API."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
from src.app.core import shared_init
from src.app.core.exceptions import global_exception_handler
from src.app.core.middlewares import setup_middleware
from src.app.home.api import router as home_router
from src.app.user.api import router as user_router
from src.app.websockets.api import router as signaling_router

env_type = os.environ.get("ENV", "development")
shared_init.load_dotenv(env_type)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    shared_init.initialize()
    yield


app = FastAPI(
    title="Conflow API",
    description="Conflow API",
    version="0.1.0",
    lifespan=lifespan,
)

setup_middleware(app)

app.include_router(home_router)
app.include_router(user_router)
app.include_router(user_router, prefix="/api")
app.include_router(signaling_router)

app.add_exception_handler(Exception, global_exception_handler)

@app.get("/scalar", include_in_schema=False)
async def scalar_html() -> HTMLResponse:
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = app.title,
    )


def main() -> None:
    """Run the development server with auto-reload."""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
