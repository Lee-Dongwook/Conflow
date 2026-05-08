"""Alembic migration environment: loads app config and SQLAlchemy metadata."""

from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Interpret the config file for Python logging.
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
from src.app.core.database import Base  # noqa: E402
from src.app.user.model import User  # noqa: E402, F401 — register model with metadata

target_metadata = Base.metadata


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
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
