from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from lms.db.models import Base
from tests.utils.database import get_diff_db_metadata, run_async_migrations


async def test_migrations_up_to_date(alembic_config, engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    await run_async_migrations(alembic_config, Base.metadata, "head")
    async with engine.connect() as connection:
        diff = await connection.run_sync(
            get_diff_db_metadata,
            metadata=(Base.metadata,),
        )
    assert not diff
