"""Alembic migration environment: loads app config and SQLAlchemy metadata."""

from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _load_dotenv_for_migrations() -> None:
    """Load server `.env.local` / `.env` so DB_* variables match the running app."""
    server_root = Path(__file__).resolve().parent.parent
    for name in (".env.local", ".env"):
        env_path = server_root / name
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_dotenv_for_migrations()

# Imports after env: database URI depends on DB_* from dotenv.
# Import every ORM class so tables register on Base.metadata before autogenerate runs.
from src.app.backlog.model import BacklogItem  # noqa: E402, F401
from src.app.board.model import BoardCard  # noqa: E402, F401
from src.app.comms.model import Channel, ChannelMember, Message  # noqa: E402, F401
from src.app.consent.model import UserConsent  # noqa: E402, F401
from src.app.core.database import Base  # noqa: E402
from src.app.core.shared import (  # noqa: E402, F401
    AuditLog,
    EntityLink,
    EventOutbox,
    Member,
    Role,
    RoleAssignment,
    Workspace,
)
from src.app.dashboard.model import DashboardConfig  # noqa: E402, F401
from src.app.hr.model import EmployeeProfile, OrgUnit  # noqa: E402, F401
from src.app.inbox.model import InboxEntry  # noqa: E402, F401
from src.app.pm.model import Issue, Project  # noqa: E402, F401
from src.app.pm.model import Sprint as PmSprint  # noqa: E402, F401
from src.app.retro.model import RetroBoard, RetroColumn, RetroItem  # noqa: E402, F401
from src.app.sprint.model import Sprint, SprintMetricSnapshot  # noqa: E402, F401
from src.app.team.model import Team, TeamMembership  # noqa: E402, F401
from src.app.user.model import User, UserProfile  # noqa: E402, F401
from src.app.week.model import WeekMilestone  # noqa: E402, F401

# Optional: CommonResource (common_resources), Agent (agent) — add when you want them migrated.
# from src.app.common.models import CommonResource  # noqa: E402, F401
# from src.app.agent.model import Agent  # noqa: E402, F401

target_metadata = Base.metadata

# Tables created by LangGraph / similar libs: ignore for autogenerate so they are not dropped.
_EXCLUDED_TABLE_NAMES = frozenset(
    {
        "checkpoint_blobs",
        "checkpoint_migrations",
        "checkpoint_writes",
        "checkpoints",
    },
)


def include_object(
    object_: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Filter objects during autogenerate (exclude third-party tables not owned by this repo)."""
    if type_ == "table" and name in _EXCLUDED_TABLE_NAMES:
        return False
    return True


def _sync_database_url() -> str:
    """Return a synchronous SQLAlchemy URL (psycopg v3) for Alembic."""
    from src.app.core.database import get_database_uri

    url = get_database_uri()
    if url.startswith("postgresql+psycopg"):
        return url
    return url.replace("postgresql://", "postgresql+psycopg://", 1)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=_sync_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = _sync_database_url()

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
