import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import SohoAccount, Student


class SohoAccountFactory(factory.Factory):
    class Meta:
        model = SohoAccount

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda o: f"example{o.id}@example.org")


@pytest.fixture
def create_soho_account(session: AsyncSession):
    async def _factory(student: Student, **kwargs) -> SohoAccount:
        soho_account = SohoAccountFactory(student=student, **kwargs)
        session.add(soho_account)
        await session.commit()
        await session.flush(soho_account)
        return soho_account

    return _factory
