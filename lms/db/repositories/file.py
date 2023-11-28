from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import VerifiedWorkFile
from lms.db.repositories.base import Repository
from lms.dto import VerifiedWorkFileData


class FileRepository(Repository[VerifiedWorkFile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=VerifiedWorkFile, session=session)

    async def get_by_google_drive_id(self, file_id: str) -> VerifiedWorkFileData | None:
        query = select(VerifiedWorkFile).filter_by(file_id=file_id)

        file = (await self._session.scalars(query)).first()
        return VerifiedWorkFileData.from_orm(file) if file else None

    async def create(
        self,
        file_id: str,
        name: str,
        url: str,
        student_id: int | None,
        subject_id: int,
    ) -> VerifiedWorkFileData:
        query = (
            insert(VerifiedWorkFile)
            .values(
                file_id=file_id,
                name=name,
                url=url,
                subject_id=subject_id,
                student_id=student_id,
            )
            .returning(VerifiedWorkFile)
        )

        try:
            result: ScalarResult[VerifiedWorkFile] = await self._session.scalars(query)
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return VerifiedWorkFileData.from_orm(result.one())
