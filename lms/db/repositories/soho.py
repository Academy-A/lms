import logging
from typing import NoReturn

from sqlalchemy import ScalarResult, insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Soho
from lms.db.repositories.base import Repository
from lms.dto import SohoData
from lms.exceptions import LMSError, SohoNotFoundError
from lms.exceptions.base import EntityNotFoundError

log = logging.getLogger(__name__)


class SohoRepository(Repository[Soho]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Soho, session=session)

    async def read_by_id(self, soho_id: int) -> SohoData:
        try:
            obj = await self._read_by_id(soho_id)
        except EntityNotFoundError as e:
            raise SohoNotFoundError from e
        return SohoData.from_orm(obj)

    async def create(self, soho_id: int, email: str, student_id: int) -> SohoData:
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
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return SohoData.from_orm(result.one())

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        log.exception("An error has occurred")
        raise LMSError from e
