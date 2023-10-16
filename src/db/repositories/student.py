from typing import Any, NoReturn

from loguru import logger
from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Student
from src.db.repositories.base import Repository
from src.exceptions import LMSError, StudentNotFoundError, StudentVKIDAlreadyUsedError


class StudentRepository(Repository[Student]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Student, session=session)

    async def read_by_vk_id(self, vk_id: int) -> Student | None:
        stmt = select(Student).where(Student.vk_id == vk_id)
        return (await self._session.scalars(stmt)).one_or_none()

    async def read_by_id(self, student_id: int) -> Student:
        student = await self._read_by_id(student_id)
        if student is None:
            raise StudentNotFoundError
        return student

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
            result: ScalarResult[Student] = await self._session.scalars(query)
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    async def update(self, *args: Any, **kwargs: Any) -> Student:
        try:
            return await self._update(*args, **kwargs)
        except NoResultFound:
            await self._session.rollback()
            raise StudentNotFoundError
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        logger.exception("An error has occurred")
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]
        if constraint == "uq__student__vk_id":
            raise StudentVKIDAlreadyUsedError from e
        raise LMSError from e
