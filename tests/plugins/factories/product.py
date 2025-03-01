from collections.abc import Callable
from datetime import date

import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Product, ProductGroup
from tests.plugins.factories.subject import SubjectFactory


class ProductGroupFactory(factory.Factory):
    class Meta:
        model = ProductGroup

    id = factory.Sequence(lambda n: n + 1)
    name = "ProductGroup-1"
    eng_name = "product_group_1"


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = "Product-1"
    start_date = date(2020, 2, 2)
    end_date = date(2020, 8, 10)
    product_group = factory.SubFactory(ProductGroupFactory)
    subject = factory.SubFactory(SubjectFactory)


@pytest.fixture
def create_product_group(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> ProductGroup:
        product_group = ProductGroupFactory(**kwargs)
        session.add(product_group)
        await session.commit()
        await session.flush(product_group)
        return product_group

    return _factory


@pytest.fixture
def create_product(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> Product:
        product = ProductFactory(**kwargs)
        session.add(product)
        await session.commit()
        await session.flush(product)
        return product

    return _factory
