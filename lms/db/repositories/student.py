import logging
from typing import Any, NoReturn

from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Student
from lms.db.repositories.base import Repository
from lms.dto import StudentDto
from lms.exceptions import LMSError, StudentNotFoundError, StudentVKIDAlreadyUsedError
from lms.exceptions.base import EntityNotFoundError

log = logging.getLogger(__name__)


class StudentRepository(Repository[Student]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Student, session=session)

    async def read_by_vk_id(self, vk_id: int) -> StudentDto | None:
        stmt = select(Student).where(Student.vk_id == vk_id)
        obj = (await self._session.scalars(stmt)).one_or_none()
        return StudentDto.from_orm(obj) if obj else None

    async def read_by_id(self, student_id: int) -> StudentDto:
        try:
            student = await self._read_by_id(student_id)
            return StudentDto.from_orm(student)
        except EntityNotFoundError as e:
            raise StudentNotFoundError from e

    async def create(
        self,
        vk_id: int,
        first_name: str | None,
        last_name: str | None,
    ) -> StudentDto:
        query = (
            insert(self._model)
            .values(vk_id=vk_id, first_name=first_name or "", last_name=last_name or "")
            .returning(self._model)
        )
        try:
            result: ScalarResult[Student] = await self._session.scalars(query)
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return StudentDto.from_orm(result.one())

    async def update(self, *args: Any, **kwargs: Any) -> StudentDto:
        try:
            obj = await self._update(*args, **kwargs)
            return StudentDto.from_orm(obj)
        except NoResultFound:
            await self._session.rollback()
            raise StudentNotFoundError
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        log.exception("An error has occurred")
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]
        if constraint == "uq__student__vk_id":
            raise StudentVKIDAlreadyUsedError from e
        raise LMSError from e
