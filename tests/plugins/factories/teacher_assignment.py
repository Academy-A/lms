from collections.abc import Callable
from datetime import datetime

import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import TeacherAssignment
from tests.plugins.factories.student import StudentProductFactory
from tests.plugins.factories.teacher import TeacherProductFactory


class TeacherAssignmentFactory(factory.Factory):
    class Meta:
        model = TeacherAssignment

    id = factory.Sequence(lambda n: n + 1)
    assignment_at = factory.LazyFunction(datetime.now)
    removed_at = None

    student_product = factory.SubFactory(StudentProductFactory)
    teacher_product = factory.SubFactory(TeacherProductFactory)


@pytest.fixture
def create_teacher_assignment(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> TeacherAssignment:
        teacher_assignment = TeacherAssignmentFactory(**kwargs)
        session.add(teacher_assignment)
        await session.commit()
        await session.flush(teacher_assignment)
        return teacher_assignment

    return _factory
