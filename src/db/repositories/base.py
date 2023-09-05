from abc import ABC
from typing import Any, Generic, NoReturn, TypeVar

from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base

Model = TypeVar("Model", bound=Base)


class Repository(ABC, Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def _read_by_id(self, object_id: int) -> Model | None:
        return await self._session.get(self._model, object_id)

    async def _update(self, *args: Any, **kwargs: Any) -> Model | None:
        stmt = update(self._model).where(*args).values(**kwargs).returning(self._model)
        result = await self._session.scalars(select(self._model).from_statement(stmt))
        await self._session.commit()
        return result.one_or_none()

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        raise NotImplementedError
