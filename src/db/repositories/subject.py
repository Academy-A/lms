from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dto import PaginationData
from src.db.models import Subject
from src.db.repositories.base import Repository
from src.exceptions import EntityNotFoundError, SubjectNotFoundError


class SubjectRepository(Repository[Subject]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Subject, session=session)

    async def paginate(self, page: int, page_size: int) -> PaginationData:
        query = select(Subject).order_by(Subject.name)
        return await self._paginate(
            query=query,
            page=page,
            page_size=page_size,
        )

    async def read_by_id(self, subject_id: int) -> Subject:
        try:
            return await self._read_by_id(subject_id)
        except EntityNotFoundError as e:
            raise SubjectNotFoundError from e