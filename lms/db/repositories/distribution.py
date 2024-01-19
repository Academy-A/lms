import logging
from typing import Any, NoReturn

from sqlalchemy import ScalarResult, insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Distribution as DistributionDb
from lms.db.repositories.base import Repository
from lms.exceptions import LMSError, SubjectNotFoundError
from lms.generals.models.distribution import Distribution

log = logging.getLogger(__name__)


class DistributionRepository(Repository[DistributionDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=DistributionDb, session=session)

    async def create(self, subject_id: int, data: dict[str, Any]) -> Distribution:
        query = (
            insert(DistributionDb)
            .values(
                subject_id=subject_id,
                data=data,
            )
            .returning(DistributionDb)
        )
        try:
            result: ScalarResult[DistributionDb] = await self._session.scalars(query)
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return Distribution.model_validate(result.one())

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        log.exception("Error has occurred")
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]
        if constraint == "":
            raise SubjectNotFoundError from e
        raise LMSError from e
