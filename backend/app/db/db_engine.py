import logging
from functools import cache
from typing import Any

from sqlalchemy import NullPool
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings

logger = logging.getLogger(__name__)


def is_database_configured() -> bool:
    """Checks if the database configuration is set."""
    settings = get_settings()
    required_attrs = [
        settings.db_host,
        settings.db_port,
        settings.db_username,
        settings.db_password,
        settings.db_name,
    ]
    return all(attr is not None for attr in required_attrs)


def get_engine(
    pool_size: int = 10, max_overflow: int = 0, database: str | None = None
) -> AsyncEngine:
    """Creates and returns an async SQLAlchemy engine with dynamic connection parameters.
    Args:
        pool_size: The size of the connection pool. If set to 0, creates a NullPool (no pooling) engine.
        max_overflow: The maximum number of connections to allow in connection pool overflow.
        database: Optional database name to connect to. If not provided, uses the default from settings
    """
    settings = get_settings()

    if not is_database_configured():
        raise RuntimeError(
            "Database configuration is incomplete or missing mandatory fields."
        )
    """Creates and returns an async SQLAlchemy engine with dynamic connection parameters.
    Args:
        pool_size: The size of the connection pool. If set to 0, creates a NullPool (no pooling) engine.
        max_overflow: The maximum number of connections to allow in connection pool overflow.
        database: Optional database name to connect to. If not provided, uses the default from settings
    """
    settings = get_settings()

    if not is_database_configured():
        raise RuntimeError(
            "Database configuration is incomplete or missing mandatory fields."
        )

    engine_kwargs: dict[str, Any] = {}
    engine_kwargs["pool_pre_ping"] = True
    if pool_size == 0:
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = pool_size
        engine_kwargs["max_overflow"] = max_overflow

    # Build the SQLAlchemy connection string
    engine = create_async_engine(
        "postgresql+asyncpg:///",
        **engine_kwargs,
    )

    @listens_for(engine.sync_engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams) -> None:  # type: ignore
        # Set up DB connection parameters
        cparams["host"] = settings.db_host
        cparams["port"] = settings.db_port
        cparams["user"] = settings.db_username
        cparams["database"] = database or settings.db_name
        logger.info(
            f"Connecting to database {cparams['database']} at {cparams['host']}:{cparams['port']} "
            f"with user {cparams['user']}"
        )
        password = settings.db_password.get_secret_value()

        cparams["password"] = password

    return engine


@cache
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    "TODO: currently used for alembic, check if can use get_session() instead"
    engine = get_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    engine = get_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
