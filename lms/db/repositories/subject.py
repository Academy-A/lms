from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Product as ProductDb
from lms.db.models import Subject as SubjectDb
from lms.db.repositories.base import PaginateMixin, Repository
from lms.exceptions import EntityNotFoundError, SubjectNotFoundError
from lms.generals.models.pagination import Pagination
from lms.generals.models.subject import ShortSubject, Subject


class SubjectRepository(PaginateMixin, Repository[SubjectDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=SubjectDb, session=session)

    async def paginate(self, page: int, page_size: int) -> Pagination[ShortSubject]:
        query = select(SubjectDb).order_by(SubjectDb.id)
        return await self._paginate(
            query=query,
            page=page,
            page_size=page_size,
            model_type=ShortSubject,
        )

    async def read_by_id(self, subject_id: int) -> Subject:
        try:
            obj = await self._read_by_id(subject_id)
        except EntityNotFoundError as e:
            raise SubjectNotFoundError from e
        return Subject.model_validate(obj)

    async def update(self, id_: int, **kwargs: Any) -> Subject:
        try:
            obj = await self._update(
                SubjectDb.id == id_,
                **kwargs,
            )
        except NoResultFound as e:
            await self._session.rollback()
            raise SubjectNotFoundError from e
        return Subject.model_validate(obj)

    async def read_all(self) -> Sequence[Subject]:
        query = select(SubjectDb).order_by(SubjectDb.id)
        result = await self._session.scalars(query)
        return [Subject.model_validate(obj) for obj in result]

    async def find_by_product(self, product_id: int) -> Subject:
        stmt = (
            select(SubjectDb)
            .join(ProductDb, SubjectDb.id == ProductDb.subject_id)
            .where(ProductDb.id == product_id)
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise SubjectNotFoundError from e
        return Subject.model_validate(obj)
