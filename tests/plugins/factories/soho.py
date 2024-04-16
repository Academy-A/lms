import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import SohoAccount
from tests.plugins.factories.student import StudentFactory


class SohoAccountFactory(factory.Factory):
    class Meta:
        model = SohoAccount

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda o: f"example{o.id}@example.org")
    student = factory.SubFactory(StudentFactory)


@pytest.fixture
def create_soho_account(session: AsyncSession):
    async def _factory(**kwargs) -> SohoAccount:
        soho_account = SohoAccountFactory(**kwargs)
        session.add(soho_account)
        await session.commit()
        await session.flush(soho_account)
        return soho_account

    return _factory
