import asyncio
import logging
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.db_engine import get_engine
from app.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("custom")


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

MIGRATIONS_LOCK_ID = 90805991
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_online() -> None:
    connectable = context.config.attributes.get("connection", None)
    if connectable is None:
        connectable = get_engine()

    if isinstance(connectable, AsyncEngine):
        asyncio.run(_run_async_flow(connectable))
    else:
        _do_run_migrations(connectable)


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def _run_async_flow(async_engine: AsyncEngine) -> None:
    """Run migration after acquiring lock"""
    async with async_engine.connect() as lock_conn:
        lock_conn = await lock_conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info(f"Acquiring advisory lock {MIGRATIONS_LOCK_ID}.")
        await lock_conn.execute(text(f"SELECT pg_advisory_lock({MIGRATIONS_LOCK_ID})"))
        logger.info(f"Lock {MIGRATIONS_LOCK_ID} acquired.")

        try:
            async with async_engine.connect() as migration_conn:
                await migration_conn.run_sync(_do_run_migrations)
        finally:
            logger.info("Migrations complete. Releasing lock.")
            await lock_conn.execute(
                text(f"SELECT pg_advisory_unlock({MIGRATIONS_LOCK_ID})")
            )
            logger.info(f"Lock {MIGRATIONS_LOCK_ID} released.")

    await async_engine.dispose()


def _do_run_migrations(sync_conn: Any) -> None:
    exclude_archive = context.get_x_argument(as_dictionary=True).get(
        "exclude_archive", "0"
    )

    # Alembic's include_object hook is untyped, so the parameters can't be annotated.
    def include_object(obj, name, type_, reflected, compare_to):  # type: ignore
        return not (
            exclude_archive == "1" and type_ == "table" and name.endswith("__archive")
        )

    context.configure(
        connection=sync_conn,
        target_metadata=target_metadata,
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
