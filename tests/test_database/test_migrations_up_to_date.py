import pytest
from celery.backends.database.session import ResultModelBase
from sqlalchemy.ext.asyncio import AsyncEngine

from lms.db.models import Base
from tests.utils.database import get_diff_db_metadata


@pytest.mark.asyncio
async def test_migrations_up_to_date(async_engine: AsyncEngine) -> None:
    async with async_engine.connect() as connection:
        diff = await connection.run_sync(
            get_diff_db_metadata,
            metadata=(Base.metadata, ResultModelBase.metadata),
        )
    assert not diff
