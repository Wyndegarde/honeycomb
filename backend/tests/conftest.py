import os
from collections.abc import AsyncIterator, Iterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from testcontainers.community.postgres import PostgresContainer

from app.constants import POSTGRES_IMAGE, POSTGRES_PORT
from app.db.db_engine import get_engine, get_session
from app.db.models import Base
from app.main import app
from app.settings import get_settings


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Throwaway Postgres, so the suite needs only a running Docker daemon."""
    with PostgresContainer(POSTGRES_IMAGE, driver=None) as pg:
        yield pg


@pytest.fixture(scope="session")
async def engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    """Engine bound to the container, with the schema created from the models."""
    # Env vars take priority over any .env file, so the dev database is never used.
    os.environ.update(
        DB_HOST=postgres_container.get_container_host_ip(),
        DB_PORT=str(postgres_container.get_exposed_port(POSTGRES_PORT)),
        DB_USERNAME=postgres_container.username,
        DB_PASSWORD=postgres_container.password,
        DB_NAME=postgres_container.dbname,
    )
    get_settings.cache_clear()

    test_engine = get_engine(pool_size=0)
    async with test_engine.begin() as conn:
        # Create all tables in the test container (requires all models are children of Base)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Session inside an outer transaction that is rolled back after each test.

    Route-level `session.commit()` calls only release a savepoint, so tests stay isolated.
    """
    async with engine.connect() as conn:
        outer = await conn.begin()
        async with AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as s:
            yield s
        await outer.rollback()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
