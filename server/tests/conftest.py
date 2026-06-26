"""Shared pytest fixtures.

Two flavors of test live under `tests/`:
  - unit tests (existing `test_*_api.py` etc.): in-process, dep-overridden,
    no real DB. They use TestClient + fakes.
  - integration tests (`tests/integration/`): hit a real PostgreSQL via the
    fixtures defined here. They share connection setup and a per-test
    workspace factory so each test gets isolated tenant data.

Integration tests require:
  - DB_USER / DB_PASSWORD / DB_NAME (and DB_HOST / DB_PORT) in env, OR
  - `.env.local` / `.env.pytest` at `server/` root.

Skip gracefully when DB env is unset so the unit suite keeps running.
"""

from __future__ import annotations

import os
import sys
import uuid as _uuid
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))


def _db_env_ready() -> bool:
    return all(
        os.environ.get(k) for k in ("DB_USER", "DB_PASSWORD", "DB_NAME")
    )


# pytest-asyncio mode is configured here so individual test modules don't need
# the `pytestmark = pytest.mark.asyncio` boilerplate.
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Skip `tests/integration/*` automatically when DB env is absent."""
    if _db_env_ready():
        return
    skip_marker = pytest.mark.skip(
        reason="Integration tests require DB_USER/DB_PASSWORD/DB_NAME env vars."
    )
    for item in items:
        if "tests/integration/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip_marker)


@pytest_asyncio.fixture(scope="session")
async def _initialized_db() -> AsyncIterator[None]:
    """Initialize the async SQLAlchemy engine once for the whole session.

    `initialize_postgres_db` is idempotent — safe to call from other code
    paths that hit the DB later in the run.
    """
    from src.app.core import database as core_db
    from src.app.core.shared_init import load_dotenv

    load_dotenv(os.environ.get("ENV", "local"))
    await core_db.initialize_postgres_db()
    yield


@pytest_asyncio.fixture
async def db_session(_initialized_db: None) -> AsyncIterator[object]:
    """Per-test SQLAlchemy AsyncSession bound to the initialized engine."""
    from src.app.core import database as core_db

    assert core_db.async_session is not None
    async with core_db.async_session() as session:
        yield session


@pytest_asyncio.fixture
async def workspace_factory(db_session: object) -> AsyncIterator[object]:
    """Returns an async callable that seeds a fresh Workspace + creator
    User/Member/RoleAssignment. Tracks created rows + cleans up on teardown.
    """
    from sqlalchemy import delete
    from src.app.core.shared import (
        AuditLog,
        EventOutbox,
        Member,
        Role,
        RoleAssignment,
        Workspace,
        WorkspaceCreateInput,
        create_workspace,
    )
    from src.app.user.model import User

    created_workspace_uuids: list[str] = []
    created_user_uuids: list[str] = []

    async def _make() -> tuple[str, str, str]:
        """Returns (workspace_uuid, member_uuid, user_uuid)."""
        user = User(
            name="pytest-runner",
            email=f"pytest-{_uuid.uuid4().hex[:8]}@example.local",
        )
        db_session.add(user)  # type: ignore[attr-defined]
        await db_session.commit()  # type: ignore[attr-defined]
        await db_session.refresh(user)  # type: ignore[attr-defined]
        created_user_uuids.append(user.uuid)

        ws = await create_workspace(
            creator_user_uuid=user.uuid,
            payload=WorkspaceCreateInput(
                name="Pytest WS",
                slug=f"pytest-{_uuid.uuid4().hex[:8]}",
            ),
            db=db_session,  # type: ignore[arg-type]
        )
        created_workspace_uuids.append(ws.uuid)

        from sqlalchemy import select

        mem_res = await db_session.execute(  # type: ignore[attr-defined]
            select(Member).where(
                Member.workspace_uuid == ws.uuid,
                Member.user_uuid == user.uuid,
            )
        )
        member = mem_res.scalar_one()
        return ws.uuid, member.uuid, user.uuid

    yield _make

    # Teardown: drop all rows we created. Bypass RLS scope by relying on
    # the per-workspace_uuid filter (also fine when RLS is off).
    for ws_uuid in created_workspace_uuids:
        for table_model in (
            EventOutbox,
            AuditLog,
            RoleAssignment,
            Role,
            Member,
            Workspace,
        ):
            col = (
                Workspace.uuid
                if table_model is Workspace
                else table_model.workspace_uuid  # type: ignore[union-attr]
            )
            await db_session.execute(  # type: ignore[attr-defined]
                delete(table_model).where(col == ws_uuid)
            )
    for user_uuid in created_user_uuids:
        await db_session.execute(  # type: ignore[attr-defined]
            delete(User).where(User.uuid == user_uuid)
        )
    await db_session.commit()  # type: ignore[attr-defined]
