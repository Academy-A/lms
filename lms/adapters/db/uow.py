from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.adapters.db.repositories.distribution import DistributionRepository
from lms.adapters.db.repositories.file import FileRepository
from lms.adapters.db.repositories.flow import FlowRepository
from lms.adapters.db.repositories.offer import OfferRepository
from lms.adapters.db.repositories.product import ProductRepository
from lms.adapters.db.repositories.reviewer import ReviewerRepository
from lms.adapters.db.repositories.setting import SettingRepository
from lms.adapters.db.repositories.soho import SohoRepository
from lms.adapters.db.repositories.student import StudentRepository
from lms.adapters.db.repositories.student_product import StudentProductRepository
from lms.adapters.db.repositories.subject import SubjectRepository
from lms.adapters.db.repositories.teacher import TeacherRepository
from lms.adapters.db.repositories.teacher_assignment import TeacherAssignmentRepository
from lms.adapters.db.repositories.teacher_product import TeacherProductRepository


class UnitOfWork:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    @asynccontextmanager
    async def start(self) -> AsyncIterator[Self]:
        async with self._sessionmaker() as session:
            self._session = session
            self.distribution = DistributionRepository(session=self._session)
            self.file = FileRepository(session=self._session)
            self.flow = FlowRepository(session=self._session)
            self.offer = OfferRepository(session=self._session)
            self.product = ProductRepository(session=self._session)
            self.reviewer = ReviewerRepository(session=self._session)
            self.setting = SettingRepository(session=self._session)
            self.soho = SohoRepository(session=self._session)
            self.student = StudentRepository(session=self._session)
            self.student_product = StudentProductRepository(session=self._session)
            self.subject = SubjectRepository(session=self._session)
            self.teacher = TeacherRepository(session=self._session)
            self.teacher_assignment = TeacherAssignmentRepository(session=self._session)
            self.teacher_product = TeacherProductRepository(session=self._session)
            yield self
            await self._session.rollback()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()
