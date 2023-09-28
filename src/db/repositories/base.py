from abc import ABC
from typing import Any, Generic, NoReturn, TypeVar

from sqlalchemy import ScalarResult, Select, func, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base
from src.db.dto import PaginationData
from src.db.mixins import DeletableMixin
from src.exceptions.base import EntityNotFoundError

Model = TypeVar("Model", bound=Base)


class Repository(ABC, Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def _read_by_id(self, object_id: int) -> Model:
        if issubclass(self._model, DeletableMixin):
            query = select(self._model).filter_by(is_deleted=False, id=object_id)
            obj = (await self._session.scalars(query)).first()
        else:
            obj = await self._session.get(self._model, object_id)
        if obj is None:
            raise EntityNotFoundError
        return obj

    async def _update(self, *args: Any, **kwargs: Any) -> Model:
        query = update(self._model).where(*args).values(**kwargs).returning(self._model)
        result = await self._session.scalars(query)
        await self._session.commit()
        return result.one()

    async def _paginate(
        self, query: Select, page: int, page_size: int
    ) -> PaginationData:
        items: ScalarResult[Model] = await self._session.scalars(
            query.limit(page_size).offset((page - 1) * page_size)
        )
        total: int = await self._session.scalar(
            select(func.count()).select_from(query.subquery())
        )  # type: ignore
        return PaginationData(
            items=items.all(),
            total=total,
            page=page,
            page_size=page_size,
        )

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        raise NotImplementedError
