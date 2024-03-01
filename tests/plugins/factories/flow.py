from collections.abc import Callable

import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Flow


class FlowFactory(factory.Factory):
    class Meta:
        model = Flow

    id = factory.Sequence(lambda n: n + 1)


@pytest.fixture
def create_flow(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> Flow:
        flow = FlowFactory(**kwargs)
        session.add(flow)
        await session.commit()
        await session.flush(flow)
        return flow

    return _factory
