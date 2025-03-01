import abc
import math
from abc import ABC
from typing import Any, Generic, NoReturn, TypeAlias, TypeVar

from pydantic import BaseModel
from sqlalchemy import ScalarResult, Select, func, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.base import Base
from lms.exceptions import EntityNotFoundError
from lms.generals.models.pagination import ItemType, MetaPageData, Pagination

Model = TypeVar("Model", bound=Base)
SchemaType: TypeAlias = type[BaseModel]


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

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        raise NotImplementedError


class PaginateMixin(abc.ABC):
    _session: AsyncSession

    async def _paginate(
        self,
        query: Select,
        page: int,
        page_size: int,
        model_type: SchemaType,
    ) -> Pagination[ItemType]:
        result: ScalarResult = await self._session.scalars(
            query.limit(page_size).offset((page - 1) * page_size)
        )
        total: int = (
            await self._session.execute(
                select(func.count()).select_from(query.subquery())
            )
        ).scalar_one()
        return Pagination[model_type](  # type: ignore[valid-type]
            items=result.all(),
            meta=MetaPageData(
                page=page,
                pages=int(math.ceil(total / page_size)) or 1,
                total=total,
                page_size=page_size,
            ),
        )
