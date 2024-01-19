from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import VerifiedWorkFile as VerifiedWorkFileDb
from lms.db.repositories.base import Repository
from lms.generals.models.verified_work_file import VerifiedWorkFile


class FileRepository(Repository[VerifiedWorkFileDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=VerifiedWorkFileDb, session=session)

    async def get_by_google_drive_id(self, file_id: str) -> VerifiedWorkFile | None:
        query = select(VerifiedWorkFileDb).filter_by(file_id=file_id)

        file = (await self._session.scalars(query)).first()
        return VerifiedWorkFile.model_validate(file) if file else None

    async def create(
        self,
        file_id: str,
        name: str,
        url: str,
        student_id: int | None,
        subject_id: int,
    ) -> VerifiedWorkFile:
        query = (
            insert(VerifiedWorkFileDb)
            .values(
                file_id=file_id,
                name=name,
                url=url,
                subject_id=subject_id,
                student_id=student_id,
            )
            .returning(VerifiedWorkFileDb)
        )

        try:
            result: ScalarResult[VerifiedWorkFileDb] = await self._session.scalars(
                query
            )
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return VerifiedWorkFile.model_validate(result.one())
