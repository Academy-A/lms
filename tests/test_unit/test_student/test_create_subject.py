import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.models import OfferFactory

pytestmark = [pytest.mark.asyncio]


async def test_create_subject(client: AsyncClient, session: AsyncSession) -> None:
    await OfferFactory.create()

    assert False


async def test_create_offer(client: AsyncClient, session: AsyncSession) -> None:
    await OfferFactory.create()
    assert True
