import time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from tests.factories.models import ProductFactory, OfferFactory

pytestmark = [pytest.mark.asyncio]


async def test_create_subject(client: AsyncClient, session: AsyncSession) -> None:
    offer = await OfferFactory.create()

    assert False


async def test_create_offer(client: AsyncClient, session: AsyncSession) -> None:
    offer = await OfferFactory.create()
    assert True
