from argparse import Namespace
from collections.abc import AsyncGenerator

from aiomisc_dependency import dependency
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lms.db.uow import UnitOfWork
from lms.db.utils import create_async_engine, create_async_session_factory


def configure_dependencies(args: Namespace) -> None:
    @dependency
    async def engine() -> AsyncGenerator[AsyncEngine, None]:
        engine = create_async_engine(
            connection_uri=args.pg_dsn,
        )
        yield engine
        await engine.dispose()

    @dependency
    async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_async_session_factory(engine=engine)

    @dependency
    async def uow(session_factory: async_sessionmaker[AsyncSession]) -> UnitOfWork:
        return UnitOfWork(session_factory)

    return