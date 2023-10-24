from abc import ABC
from typing import Any, Generic, NoReturn, TypeVar

from sqlalchemy import ScalarResult, Select, func, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.base import Base
from lms.dto import PaginationData
from lms.exceptions import EntityNotFoundError

Model = TypeVar("Model", bound=Base)


class Repository(ABC, Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def _read_by_id(self, object_id: int) -> Model:
        obj = await self._session.get(self._model, object_id)
        if obj is None:
            raise EntityNotFoundError
        return obj

    async def _update(self, *args: Any, **kwargs: Any) -> Model:
        query = update(self._model).where(*args).values(**kwargs).returning(self._model)
        result = await self._session.scalars(query)
        await self._session.flush()
        return result.one()

    async def save(self, obj: Model) -> Model:
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

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
