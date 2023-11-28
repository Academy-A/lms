from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Product, Subject
from lms.db.repositories.base import Repository
from lms.dto import PaginationData, SubjectDto
from lms.exceptions import EntityNotFoundError, SubjectNotFoundError


class SubjectRepository(Repository[Subject]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Subject, session=session)

    async def paginate(self, page: int, page_size: int) -> PaginationData:
        query = select(Subject).order_by(Subject.id)
        return await self._paginate(
            query=query,
            page=page,
            page_size=page_size,
            dto=SubjectDto,
        )

    async def read_by_id(self, subject_id: int) -> SubjectDto:
        try:
            obj = await self._read_by_id(subject_id)
            return SubjectDto.from_orm(obj)
        except EntityNotFoundError as e:
            raise SubjectNotFoundError from e

    async def find_by_product(self, product_id: int) -> SubjectDto:
        stmt = (
            select(Subject)
            .join(Product, Subject.id == Product.subject_id)
            .where(Product.id == product_id)
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
            return SubjectDto.from_orm(obj)
        except NoResultFound as e:
            raise SubjectNotFoundError from e
