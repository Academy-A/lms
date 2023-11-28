from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.db.repositories.file import FileRepository
from lms.db.repositories.flow import FlowRepository
from lms.db.repositories.offer import OfferRepository
from lms.db.repositories.product import ProductRepository
from lms.db.repositories.setting import SettingRepository
from lms.db.repositories.soho import SohoRepository
from lms.db.repositories.student import StudentRepository
from lms.db.repositories.student_product import StudentProductRepository
from lms.db.repositories.subject import SubjectRepository
from lms.db.repositories.teacher import TeacherRepository
from lms.db.repositories.teacher_assignment import TeacherAssignmentRepository
from lms.db.repositories.teacher_product import TeacherProductRepository


class UnitOfWork:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    async def __aenter__(self) -> Self:
        self._session = self._sessionmaker()
        self.file = FileRepository(session=self._session)
        self.flow = FlowRepository(session=self._session)
        self.offer = OfferRepository(session=self._session)
        self.product = ProductRepository(session=self._session)
        self.setting = SettingRepository(session=self._session)
        self.soho = SohoRepository(session=self._session)
        self.student = StudentRepository(session=self._session)
        self.student_product = StudentProductRepository(session=self._session)
        self.subject = SubjectRepository(session=self._session)
        self.teacher = TeacherRepository(session=self._session)
        self.teacher_assignment = TeacherAssignmentRepository(session=self._session)
        self.teacher_product = TeacherProductRepository(session=self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._session.rollback()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()
