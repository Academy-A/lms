import os
from collections.abc import AsyncGenerator
from types import SimpleNamespace

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from lms.adapters.db.base import Base
from lms.adapters.db.repositories.reviewer import ReviewerRepository
from lms.adapters.db.uow import UnitOfWork
from lms.adapters.db.utils import create_async_engine, make_alembic_config
from tests.plugins.factories.factories import factories


@pytest.fixture(scope="session")
def pg_dsn(localhost) -> str:
    default = f"postgresql+asyncpg://pguser:pgpass@{localhost}:5432/pgdb"
    return os.getenv("APP_PG_DSN", default)


@pytest.fixture(scope="session")
def alembic_config(pg_dsn: str) -> AlembicConfig:
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options, dsn=pg_dsn)


@pytest.fixture
async def engine(pg_dsn: str) -> AsyncGenerator[AsyncEngine, None]:
    async with create_async_engine(pg_dsn) as engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield engine


@pytest.fixture
async def sessionmaker(engine: AsyncEngine):
    yield async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture
async def session(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        for factory in factories:
            factory.__async_session__ = session
        yield session


@pytest.fixture
def uow(sessionmaker) -> UnitOfWork:
    return UnitOfWork(sessionmaker=sessionmaker)


@pytest.fixture
def reviewer_repository(session: AsyncSession) -> ReviewerRepository:
    return ReviewerRepository(session=session)
