import os
from collections.abc import AsyncGenerator
from types import SimpleNamespace

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from lms.db.base import Base
from lms.db.uow import UnitOfWork
from lms.db.utils import make_alembic_config
from tests.plugins.factories import factories
from tests.utils.database import clear_db, prepare_new_database, run_async_migrations


@pytest.fixture(scope="session")
def db_name() -> str:
    default = "test_lms"
    return os.getenv("APP_PG_DB_NAME", default)


@pytest.fixture(scope="session")
def stairway_db_name() -> str:
    return "stairway"


@pytest.fixture(scope="session")
def pg_dsn(localhost, db_name: str) -> str:
    default = f"postgresql+asyncpg://pguser:pgpass@{localhost}:5432/{db_name}"
    return os.getenv("APP_PG_DSN", default)


@pytest.fixture(scope="session")
def base_pg_dsn(localhost) -> str:
    default = f"postgresql+asyncpg://pguser:pgpass@{localhost}:5432/postgres"
    return os.getenv("APP_BASE_PG_DSN", default)


@pytest.fixture(scope="session")
def alembic_config(pg_dsn: str) -> AlembicConfig:
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_dsn=pg_dsn,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


@pytest.fixture
async def async_engine(
    base_pg_dsn: str,
    pg_dsn: str,
    db_name: str,
    alembic_config: AlembicConfig,
    stairway_db_name: str,
):
    await prepare_new_database(base_pg_dsn=base_pg_dsn, new_database=db_name)
    await prepare_new_database(base_pg_dsn=base_pg_dsn, new_database=stairway_db_name)
    await run_async_migrations(alembic_config, Base.metadata, "head")
    engine = create_async_engine(pg_dsn)
    yield engine
    await engine.dispose()


@pytest.fixture
async def sessionmaker(async_engine: AsyncEngine):
    yield async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture(autouse=True, scope="function")
async def session(
    sessionmaker: async_sessionmaker[AsyncSession],
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        for factory in factories:
            factory.__async_session__ = session
        yield session
    await clear_db(async_engine)


@pytest.fixture()
async def uow(sessionmaker) -> UnitOfWork:
    return UnitOfWork(sessionmaker=sessionmaker)
