import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Reviewer


class ReviewerFactory(factory.Factory):
    class Meta:
        model = Reviewer

    id = factory.Sequence(lambda n: n + 1)
    subject_id = factory.Sequence(lambda n: n + 1)
    first_name = "First"
    last_name = "Last"
    email = "a@a.ru"
    desired = 10
    max_ = 20
    min_ = 5
    abs_max = 30
    is_active = True


@pytest.fixture
async def create_reviewer(session: AsyncSession):
    async def _factory(**kwargs):
        reviewer = ReviewerFactory(**kwargs)
        session.add(reviewer)
        await session.commit()
        await session.flush(reviewer)
        return reviewer

    return _factory
