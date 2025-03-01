import logging
from typing import NoReturn

from sqlalchemy import ScalarResult, insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import SohoAccount as SohoAccountDb
from lms.adapters.db.repositories.base import Repository
from lms.exceptions import LMSError, SohoNotFoundError
from lms.exceptions.base import EntityNotFoundError
from lms.generals.models.soho import SohoAccount

log = logging.getLogger(__name__)


class SohoRepository(Repository[SohoAccountDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=SohoAccountDb, session=session)

    async def read_by_id(self, soho_id: int) -> SohoAccount:
        try:
            obj = await self._read_by_id(soho_id)
        except EntityNotFoundError as e:
            raise SohoNotFoundError from e
        return SohoAccount.model_validate(obj)

    async def create(self, soho_id: int, email: str, student_id: int) -> SohoAccount:
        query = (
            insert(SohoAccountDb)
            .values(
                id=soho_id,
                email=email,
                student_id=student_id,
            )
            .returning(SohoAccountDb)
        )
        try:
            result: ScalarResult[SohoAccountDb] = await self._session.scalars(query)
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return SohoAccount.model_validate(result.one())

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        log.exception("An error has occurred")
        raise LMSError from e
