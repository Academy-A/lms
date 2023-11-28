import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path
from types import SimpleNamespace

import pytest
import pytest_asyncio
from alembic.config import Config as AlembicConfig
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from lms.api.services import generate_token
from lms.config import Settings
from lms.db.models import Base
from lms.db.utils import make_alembic_config
from lms.setup_app import get_application
from tests.factories import factories
from tests.utils import clear_db, prepare_new_database, run_async_migrations


@pytest.fixture(scope="session")
def project_path() -> Path:
    return Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def stairway_db() -> str:
    return "stairway"


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(POSTGRES_DB="test_lms_database")


@pytest.fixture(scope="session")
def alembic_config(settings: Settings) -> AlembicConfig:
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_url=settings.build_db_connection_uri(),
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


@pytest_asyncio.fixture(scope="session")
async def async_engine(
    settings: Settings, alembic_config: AlembicConfig, stairway_db: str
):
    await prepare_new_database(settings=settings, new_database=settings.POSTGRES_DB)
    await prepare_new_database(settings=settings, new_database=stairway_db)
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


@pytest_asyncio.fixture(autouse=True)
async def session(
    sessionmaker: async_sessionmaker[AsyncSession],
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        session: AsyncSession = sessionmaker()
        for factory in factories:
            factory.__async_session__ = session
        yield session
    finally:
        await session.close()
        await clear_db(async_engine)


@pytest_asyncio.fixture(scope="session")
async def client(
    settings: Settings,
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    app = get_application(settings=settings)
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def token(settings: Settings) -> str:
    return generate_token(data={"test_data": True}, secret_key=settings.SECRET_KEY)
