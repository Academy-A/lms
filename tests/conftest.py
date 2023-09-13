import asyncio
from pathlib import Path
from typing import AsyncGenerator
from httpx import AsyncClient
import pytest

from alembic.config import Config as AlembicConfig
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from src.config import Settings
from src.db.models import Base
from src.setup_app import get_appliation
from tests.factories.models import factories
from tests.utils import prepare_new_database, run_async_migrations

PROJECT_PATH = Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    settings = Settings()
    settings.POSTGRES_DB = "test_" + settings.POSTGRES_DB
    return settings


@pytest.fixture(scope="session")
def alembic_config(settings: Settings) -> AlembicConfig:
    alembic_cfg = AlembicConfig(PROJECT_PATH / "src/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.build_db_connection_uri())
    return alembic_cfg


@pytest_asyncio.fixture(scope="session")
async def async_engine(settings: Settings, alembic_config: AlembicConfig):
    await prepare_new_database(settings=settings)
    await run_async_migrations(alembic_config, Base.metadata, "head")
    engine = create_async_engine(settings.build_db_connection_uri())
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def sessionmaker(async_engine: AsyncEngine):
    yield async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest_asyncio.fixture
async def session(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    try:
        session: AsyncSession = sessionmaker()

        for factory in factories:
            factory._meta.sqlalchemy_session = session
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture(scope="session")
async def client(
    settings: Settings, async_engine: AsyncEngine
) -> AsyncGenerator[AsyncClient, None]:
    app = get_appliation(settings=settings)
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
