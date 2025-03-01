import logging
from typing import NoReturn

from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Student as StudentDb
from lms.adapters.db.repositories.base import Repository
from lms.exceptions import LMSError, StudentNotFoundError, StudentVKIDAlreadyUsedError
from lms.exceptions.base import EntityNotFoundError
from lms.generals.models.student import Student

log = logging.getLogger(__name__)


class StudentRepository(Repository[StudentDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=StudentDb, session=session)

    async def read_by_vk_id(self, vk_id: int) -> Student | None:
        stmt = select(StudentDb).where(StudentDb.vk_id == vk_id)
        obj = (await self._session.scalars(stmt)).one_or_none()
        return Student.model_validate(obj) if obj else None

    async def read_by_id(self, student_id: int) -> Student:
        try:
            student = await self._read_by_id(student_id)
            return Student.model_validate(student)
        except EntityNotFoundError as e:
            raise StudentNotFoundError from e

    async def create(
        self,
        vk_id: int,
        first_name: str | None,
        last_name: str | None,
    ) -> Student:
        query = (
            insert(self._model)
            .values(vk_id=vk_id, first_name=first_name or "", last_name=last_name or "")
            .returning(self._model)
        )
        try:
            result: ScalarResult[StudentDb] = await self._session.scalars(query)
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return Student.model_validate(result.one())

    async def update_vk_id(self, student_id: int, vk_id: int) -> Student:
        try:
            obj = await self._update(StudentDb.id == student_id, vk_id=vk_id)
        except NoResultFound:
            await self._session.rollback()
            raise StudentNotFoundError
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        return Student.model_validate(obj)

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        log.exception("An error has occurred")
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]
        if constraint == "uq__student__vk_id":
            raise StudentVKIDAlreadyUsedError from e
        raise LMSError from e
