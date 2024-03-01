from collections.abc import Callable
from datetime import datetime

import factory
import pytest
from factory import fuzzy
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import (
    Flow,
    Product,
    StudentProduct,
    Teacher,
    TeacherAssignment,
    TeacherProduct,
    TeacherProductFlow,
)
from lms.generals.enums import TeacherType


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


class TeacherProductFlowFactory(factory.Factory):
    class Meta:
        model = TeacherProductFlow

    id = factory.Sequence(lambda n: n + 1)


class TeacherAssignmentFactory(factory.Factory):
    class Meta:
        model = TeacherAssignment

    id = factory.Sequence(lambda n: n + 1)
    assignment_at = factory.LazyFunction(datetime.now)
    removed_at = None


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
    async def _factory(teacher: Teacher, product: Product, **kwargs):
        teacher_product: TeacherProduct = TeacherProductFactory(
            teacher=teacher,
            product=product,
            **kwargs,
        )
        session.add(teacher_product)
        await session.commit()
        await session.flush(teacher_product)
        return teacher_product

    return _factory


@pytest.fixture
def create_teacher_product_flow(session: AsyncSession) -> Callable:
    async def _factory(
        teacher_product: TeacherProduct,
        flow: Flow,
        **kwargs,
    ) -> TeacherProductFlow:
        teacher_product_flow = TeacherProductFlowFactory(
            teacher_product=teacher_product,
            flow=flow,
            **kwargs,
        )
        session.add(teacher_product_flow)
        await session.commit()
        await session.flush(teacher_product_flow)
        return teacher_product_flow

    return _factory


@pytest.fixture
def create_teacher_assignment(session: AsyncSession) -> Callable:
    async def _factory(
        student_product: StudentProduct,
        teacher_product: TeacherProduct,
        **kwargs,
    ) -> TeacherAssignment:
        teacher_assignment = TeacherAssignmentFactory(
            student_product=student_product,
            teacher_product=teacher_product,
            **kwargs,
        )
        session.add(teacher_assignment)
        await session.commit()
        await session.flush(teacher_assignment)
        return teacher_assignment

    return _factory
