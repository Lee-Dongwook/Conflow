"""ASGI entrypoint for the Conflow API."""

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

# Models without active routers — imported so SQLAlchemy resolves all relationships
import src.app.retro.model  # noqa: F401
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
from src.app.agent.api import router as agent_router
from src.app.backlog.api import router as backlog_router
from src.app.board.api import router as board_router
from src.app.comms.api import router as comms_router
from src.app.consent.api import router as consent_router
from src.app.core import database as core_db
from src.app.core import shared_init
from src.app.core.exceptions import global_exception_handler
from src.app.core.middlewares import setup_middleware
from src.app.core.outbox import outbox_worker_loop
from src.app.core.runtime import logger
from src.app.core.shared.api import router as workspace_router
from src.app.dashboard.api import router as dashboard_router
from src.app.home.api import router as home_router
from src.app.hr.api import router as hr_router
from src.app.pm.api import router as pm_router
from src.app.sprint.api import router as sprint_router
from src.app.survey.api import router as survey_router
from src.app.team.api import router as team_router
from src.app.user.api import router as user_router
from src.app.websockets.api import router as signaling_router
from src.app.week.api import router as week_router

env_type = os.environ.get("ENV", "development")
shared_init.load_dotenv(env_type)

_OUTBOX_WORKER_ENV = "CONFLOW_OUTBOX_WORKER_ENABLED"


def _outbox_worker_enabled() -> bool:
    return os.environ.get(_OUTBOX_WORKER_ENV, "true").lower() in ("1", "true", "yes", "on")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    shared_init.initialize()

    # Subscriber registrations import their handlers at module import time;
    # importing here keeps the registry populated before the worker loop polls.
    import src.app.core.outbox_subscribers  # noqa: F401, PLC0415

    worker_task: asyncio.Task[None] | None = None
    if _outbox_worker_enabled():
        try:
            await core_db.initialize_postgres_db()
        except Exception:
            logger.exception("DB init failed; outbox worker disabled")
        else:
            session_factory = core_db.async_session
            if session_factory is None:
                logger.warning("async_session unavailable; outbox worker disabled")
            else:
                worker_task = asyncio.create_task(
                    outbox_worker_loop(session_factory),
                    name="outbox-worker",
                )
                logger.info("outbox worker task scheduled")
    else:
        logger.info("outbox worker disabled via %s", _OUTBOX_WORKER_ENV)

    try:
        yield
    finally:
        if worker_task is not None:
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass


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
app.include_router(consent_router)
app.include_router(consent_router, prefix="/api")
app.include_router(agent_router)
app.include_router(agent_router, prefix="/api")
app.include_router(team_router)
app.include_router(team_router, prefix="/api")
app.include_router(dashboard_router)
app.include_router(dashboard_router, prefix="/api")
app.include_router(sprint_router)
app.include_router(sprint_router, prefix="/api")
app.include_router(backlog_router)
app.include_router(backlog_router, prefix="/api")
app.include_router(board_router)
app.include_router(board_router, prefix="/api")
app.include_router(survey_router)
app.include_router(survey_router, prefix="/api")
app.include_router(week_router)
app.include_router(week_router, prefix="/api")
app.include_router(workspace_router)
app.include_router(workspace_router, prefix="/api")
app.include_router(pm_router)
app.include_router(pm_router, prefix="/api")
app.include_router(comms_router)
app.include_router(comms_router, prefix="/api")
app.include_router(hr_router)
app.include_router(hr_router, prefix="/api")
app.include_router(signaling_router)

app.add_exception_handler(Exception, global_exception_handler)


@app.get("/", include_in_schema=False)
async def health_check():
    return {"status": "ok"}


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html() -> HTMLResponse:
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


def main() -> None:
    """Run the development server with auto-reload."""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
