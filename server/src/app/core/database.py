import os
import urllib.parse
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, TypeVar, cast

from sqlalchemy.orm import DeclarativeBase

from . import logger

if TYPE_CHECKING:
    from psycopg import AsyncConnection
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
    from supabase import AsyncClient as SupabaseClient

supabase_client: "SupabaseClient | None" = None
async_engine: "AsyncEngine | None" = None
async_session: "async_sessionmaker[AsyncSession] | None" = None
DB_URI: str | None = None
ASYNC_DB_URI: str | None = None

def get_database_uri() -> str:
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME")

    if not all([db_user, db_password, db_name]):
        raise RuntimeError("DataBase Environment Variables are not set")

    CONNECT_TIMEOUT = 30 # noqa: N806
    encoded_db_password = urllib.parse.quote_plus(cast("str", db_password))

    db_uri = (
        f"postgresql://{db_user}:{encoded_db_password}@{db_host}:{db_port}/{db_name}"
        f"?sslmode=prefer"
        f"&gssencmode=disable"
        f"&connect_timeout={CONNECT_TIMEOUT}"
    )
    return db_uri

async def initialize_postgres_db() -> None:
    global async_session, async_engine
    global supabase_client, DB_URI, ASYNC_DB_URI

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool
    from supabase import acreate_client
    from supabase.lib.client_options import AsyncClientOptions as ClientOptions

    DB_URI = get_database_uri()
    ASYNC_DB_URI = DB_URI.replace("postgresql://", "postgresql+psycopg_async://") # noqa: N806

    if async_session is not None:
        return
    
    pool_class_type = os.environ.get("DB_POOL_CLASS", "queue").lower()

    engine_kwargs = {
        "pool_pre_ping": True,
        "connect_args": {
            "keepalives": int(os.environ.get("DB_KEEPALIVES", "1")),
            "keepalives_idle": int(os.environ.get("DB_KEEPALIVES_IDLE", "30")),
            "keepalives_interval": int(os.environ.get("DB_KEEPALIVES_INTERVAL", "10")),
            "keepalives_count": int(os.environ.get("DB_KEEPALIVES_COUNT", "3")),
        }
    }

    if pool_class_type == "null": 
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs.update({
            "pool_use_lifo": os.environ.get("DB_POOL_USE_LIFO", "true").lower() in ["1", "true"],
            "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
            "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
            "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "600")),
        })

    async_engine = create_async_engine(
        ASYNC_DB_URI,
        **engine_kwargs,
    )

    async_session = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
    )
    
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")
    supabase_client = await acreate_client(supabase_url, supabase_key, ClientOptions(storage_client_timeout=30))  # noqa: E501


async def initialize_database() -> None:
    from . import base  # noqa: F401
    
    # --- asyncpg Monkey Patch ---
    try:
        import asyncpg
        from asyncpg.pool import Pool

        if not hasattr(asyncpg, "_lb_patched"):
            orig_create_pool = asyncpg.create_pool
            orig_connect = asyncpg.connect

            pg_timeout = float(os.environ.get("ASYNCPG_COMMAND_TIMEOUT", "60.0"))

            def _inject_asyncpg_settings(kwargs: dict[str, Any]) -> dict[str, Any]:
                if "command_timeout" not in kwargs:
                    kwargs["command_timeout"] = pg_timeout
                
                server_settings = kwargs.get("server_settings", {})
                server_settings.update({
                    "tcp_keepalives_idle": str(int(os.environ.get("DB_TCP_KEEPALIVES_IDLE", "300"))),
                    "tcp_keepalives_interval": str(int(os.environ.get("DB_TCP_KEEPALIVES_INTERVAL", "30"))),  # noqa: E501
                    "tcp_keepalives_count": str(int(os.environ.get("DB_TCP_KEEPALIVES_COUNT", "3"))),  # noqa: E501
                })
                kwargs["server_settings"] = server_settings
                return kwargs
            
            async def patched_create_pool(*args: Any, **kwargs: Any) -> Pool:
                return await orig_create_pool(*args, **_inject_asyncpg_settings(kwargs))

            async def patched_connect(*args: Any, **kwargs: Any) -> Any:
                return await orig_connect(*args, **_inject_asyncpg_settings(kwargs))

            asyncpg.create_pool = patched_create_pool
            asyncpg.connect = patched_connect
            setattr(asyncpg, "_lb_patched", True)
            logger.info("AsyncPG connection pool settings patched for keepalives")
    except ImportError:
        pass

    await initialize_postgres_db()

@asynccontextmanager
async def get_connection() -> AsyncGenerator["AsyncConnection[dict[str, Any]]"]:
    from psycopg import AsyncConnection
    from psycopg.rows import dict_row

    conn: AsyncConnection[dict[str, Any]] | None = None
    try:
        if not DB_URI:
            raise RuntimeError("Database URI is not initialized")
        conn = await AsyncConnection.connect(
            DB_URI,
            autocommit=False,
            row_factory=dict_row,
        )
        yield conn
    except Exception:
        raise
    finally:
        if conn is not None:
            await conn.close()

@asynccontextmanager
async def async_context_session() -> AsyncGenerator["AsyncSession"]:
    if async_session is None:
        await initialize_postgres_db()

    session_factory = cast("Callable[[], AsyncSession]", async_session)
    async with session_factory() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()



async def get_async_db() -> AsyncGenerator["AsyncSession"]:
    if async_session is None:
        await initialize_postgres_db()

    session_factory = cast("Callable[[], AsyncSession]", async_session)
    async with session_factory() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()


T = TypeVar("T")

class Base(DeclarativeBase):
    pass

