from collections.abc import Callable
from datetime import datetime

import factory
import pytest
from factory import fuzzy
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Flow, Offer, Product, Student, StudentProduct, TeacherProduct
from lms.generals.enums import TeacherType


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
    teacher_type = fuzzy.FuzzyChoice(list(TeacherType) + [None])
    cohort = 1
    teacher_grade = 5
    teacher_graded_at = factory.LazyFunction(datetime.now)
    expulsion_at = None


@pytest.fixture
def create_student(session: AsyncSession) -> Callable:
    async def _factory(**kwargs):
        student = StudentFactory(**kwargs)
        session.add(student)
        await session.commit()
        await session.flush(student)
        return student

    return _factory


@pytest.fixture
def create_student_product(session: AsyncSession) -> Callable:
    async def _factory(
        student: Student,
        product: Product,
        offer: Offer,
        flow: Flow,
        teacher_product: TeacherProduct | None = None,
        **kwargs,
    ) -> StudentProduct:
        student_product: StudentProduct = StudentProductFactory(
            student=student,
            product=product,
            teacher_product=teacher_product,
            offer=offer,
            flow=flow,
            **kwargs,
        )
        session.add(student_product)
        await session.commit()
        await session.flush(student_product)
        return student_product

    return _factory
