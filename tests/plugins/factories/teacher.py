from collections.abc import Callable

import factory
import pytest
from factory import fuzzy
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import (
    Teacher,
    TeacherProduct,
    TeacherProductFlow,
)
from lms.generals.enums import TeacherType
from tests.plugins.factories.flow import FlowFactory
from tests.plugins.factories.product import ProductFactory


class TeacherFactory(factory.Factory):
    class Meta:
        model = Teacher

    id = factory.Sequence(lambda n: n + 1)
    first_name = "First"
    last_name = "Last"
    vk_id = factory.Sequence(lambda n: n + 1)


class TeacherProductFactory(factory.Factory):
    class Meta:
        model = TeacherProduct

    id = factory.Sequence(lambda n: n + 1)
    type = fuzzy.FuzzyChoice(list(TeacherType))
    is_active = True
    max_students = 20
    average_grade = 5
    grade_counter = 1
    teacher = factory.SubFactory(TeacherFactory)
    product = factory.SubFactory(ProductFactory)


class TeacherProductFlowFactory(factory.Factory):
    class Meta:
        model = TeacherProductFlow

    id = factory.Sequence(lambda n: n + 1)
    teacher_product = factory.SubFactory(TeacherProductFactory)
    flow = factory.SubFactory(FlowFactory)


@pytest.fixture
def create_teacher(session: AsyncSession) -> Callable:
    async def _factory(**kwargs):
        teacher = TeacherFactory(**kwargs)
        session.add(teacher)
        await session.commit()
        await session.flush(teacher)
        return teacher

    return _factory


@pytest.fixture
def create_teacher_product(session: AsyncSession) -> Callable:
    async def _factory(**kwargs):
        teacher_product: TeacherProduct = TeacherProductFactory(**kwargs)
        session.add(teacher_product)
        await session.commit()
        await session.refresh(teacher_product)
        return teacher_product

    return _factory


@pytest.fixture
def create_teacher_product_flow(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> TeacherProductFlow:
        teacher_product_flow = TeacherProductFlowFactory(**kwargs)
        session.add(teacher_product_flow)
        await session.commit()
        await session.flush(teacher_product_flow)
        return teacher_product_flow

    return _factory
