from typing import NoReturn

from loguru import logger
from sqlalchemy import ScalarResult, insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Soho
from src.db.repositories.base import Repository
from src.exceptions import LMSError, SohoNotFoundError
from src.exceptions.base import EntityNotFoundError


class SohoRepository(Repository[Soho]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Soho, session=session)

    async def read_by_id(self, soho_id: int) -> Soho:
        try:
            return await self._read_by_id(soho_id)
        except EntityNotFoundError as e:
            raise SohoNotFoundError from e

    async def create(self, soho_id: int, email: str, student_id: int) -> Soho:
        query = (
            insert(Soho)
            .values(
                id=soho_id,
                email=email,
                student_id=student_id,
            )
            .returning(Soho)
        )
        try:
            result: ScalarResult[Soho] = await self._session.scalars(query)
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        logger.exception("An error has occurred")
        raise LMSError from e
