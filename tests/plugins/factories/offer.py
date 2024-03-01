from collections.abc import Callable

import factory
import pytest
from factory import fuzzy
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Offer, Product
from lms.generals.enums import TeacherType


class OfferFactory(factory.Factory):
    class Meta:
        model = Offer

    id = factory.Sequence(lambda n: n + 1)
    name = "Offer-1"
    cohort = 1
    teacher_type = fuzzy.FuzzyChoice(list(TeacherType) + [None])


@pytest.fixture
def create_offer(session: AsyncSession) -> Callable:
    async def _factory(product: Product, **kwargs) -> Offer:
        offer = OfferFactory(product=product, **kwargs)
        session.add(offer)
        await session.commit()
        await session.flush(offer)
        return offer

    return _factory
