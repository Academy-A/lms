from collections.abc import Callable
from datetime import datetime

import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Student, StudentProduct
from lms.generals.enums import TeacherType
from tests.plugins.factories.flow import FlowFactory
from tests.plugins.factories.offer import OfferFactory
from tests.plugins.factories.product import ProductFactory
from tests.plugins.factories.teacher import TeacherProductFactory


class StudentFactory(factory.Factory):
    class Meta:
        model = Student

    id = factory.Sequence(lambda n: n + 1)
    first_name = "First"
    last_name = "Last"
    vk_id = factory.Sequence(lambda n: n + 1)


class StudentProductFactory(factory.Factory):
    class Meta:
        model = StudentProduct

    id = factory.Sequence(lambda n: n + 1)
    teacher_type = TeacherType.CURATOR
    cohort = 1
    teacher_grade = 5
    teacher_graded_at = factory.LazyFunction(datetime.now)
    expulsion_at = None
    student = factory.SubFactory(StudentFactory)
    teacher_product = factory.SubFactory(
        TeacherProductFactory,
        type=TeacherType.CURATOR,
    )
    offer = factory.SubFactory(
        OfferFactory,
        teacher_type=TeacherType.CURATOR,
    )
    product = factory.SubFactory(ProductFactory)
    flow = factory.SubFactory(FlowFactory)


@pytest.fixture
def create_student(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> Student:
        student = StudentFactory(**kwargs)
        session.add(student)
        await session.commit()
        await session.flush(student)
        return student

    return _factory


@pytest.fixture
def create_student_product(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> StudentProduct:
        student_product: StudentProduct = StudentProductFactory(**kwargs)
        session.add(student_product)
        await session.commit()
        await session.flush(student_product)
        return student_product

    return _factory
