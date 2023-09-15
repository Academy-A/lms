import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.config import Settings
from src.db.factory import create_async_engine

logger = logging.getLogger(__name__)


async def check_connection(engine: AsyncEngine) -> None:
    async with AsyncSession(engine) as session:
        await session.execute(select(1))


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Start check database connection")
    settings = Settings()
    while True:
        try:
            engine = create_async_engine(
                connection_uri=settings.build_db_connection_uri(), pool_pre_ping=True
            )
            await check_connection(engine)
            logger.info("Database started")
            return
        except:
            logger.info("Not connected")
            await asyncio.sleep(5)
            logger.info("Retry after 5 sec")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
