from collections.abc import AsyncGenerator, Callable
from typing import Any
from fastapi import BackgroundTasks

from sqlalchemy import Engine, create_engine as sa_create_engine
from sqlalchemy.orm import sessionmaker
import orjson
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine as sa_create_async_engine,
)

from src.db.provider import DatabaseProvider


def create_async_engine(connection_uri: str, **engine_kwargs: Any) -> AsyncEngine:
    if engine_kwargs.get("json_serializer") is None:
        engine_kwargs["json_serializer"] = orjson.dumps
    if engine_kwargs.get("json_deserializer") is None:
        engine_kwargs["json_deserializer"] = orjson.loads
    return sa_create_async_engine(url=connection_uri, **engine_kwargs)


def create_async_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def create_provider(
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[BackgroundTasks], AsyncGenerator[DatabaseProvider, None]]:
    async def wrapper(
        background_tasks: BackgroundTasks,
    ) -> AsyncGenerator[DatabaseProvider, None]:
        async with session_factory() as session:
            yield DatabaseProvider(session=session, background_tasks=background_tasks)

    return wrapper


def create_engine(connection_uri: str, **engine_kwargs: Any) -> Engine:
    if engine_kwargs.get("json_serializer") is None:
        engine_kwargs["json_serializer"] = orjson.dumps
    if engine_kwargs.get("json_deserializer") is None:
        engine_kwargs["json_deserializer"] = orjson.loads
    return sa_create_engine(url=connection_uri, **engine_kwargs)


def create_session_factory(
    engine: Engine,
) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
