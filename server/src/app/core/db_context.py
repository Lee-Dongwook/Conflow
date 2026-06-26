"""Per-transaction RLS context variables.

Postgres RLS policies created by `alembic/manual_sql/rls_policies.sql`
consult `current_setting('app.workspace_uuid')` (and optionally
`current_setting('app.member_uuid')`). This module is the only sanctioned
way to set them — service code should always go through `set_workspace_context`
on the very first DB operation in a request.

`SET LOCAL` scopes the value to the current transaction; once SQLAlchemy
commits/rolls back, the setting is dropped. Each request that starts a
fresh `AsyncSession` therefore must re-set it.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_workspace_context(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str | None = None,
) -> None:
    """Set `app.workspace_uuid` (and optionally `app.member_uuid`) on the
    open transaction. Idempotent — safe to call multiple times per request.
    """
    await db.execute(
        text("SET LOCAL app.workspace_uuid = :ws"),
        {"ws": workspace_uuid},
    )
    if member_uuid is not None:
        await db.execute(
            text("SET LOCAL app.member_uuid = :mb"),
            {"mb": member_uuid},
        )


@asynccontextmanager
async def workspace_context(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    member_uuid: str | None = None,
) -> AsyncIterator[None]:
    """`async with` variant for ad-hoc scripts and tests.

    Production request lifecycle should call `set_workspace_context`
    directly from the dep/middleware that resolves the caller's Member.
    """
    await set_workspace_context(
        db, workspace_uuid=workspace_uuid, member_uuid=member_uuid
    )
    yield
