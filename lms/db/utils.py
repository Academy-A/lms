import os
from argparse import Namespace
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from enum import StrEnum
from pathlib import Path
from typing import Any

import orjson
import sqlalchemy.dialects.postgresql as pg
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as sa_create_async_engine

import lms
from lms.utils.http import dumps

PROJECT_PATH = Path(lms.__file__).parent.parent.resolve()


@asynccontextmanager
async def create_async_engine(
    connection_uri: str, **engine_kwargs: Any
) -> AsyncIterator[AsyncEngine]:
    if engine_kwargs.get("json_serializer") is None:
        engine_kwargs["json_serializer"] = dumps
    if engine_kwargs.get("json_deserializer") is None:
        engine_kwargs["json_deserializer"] = orjson.loads
    engine = sa_create_async_engine(url=connection_uri, **engine_kwargs)
    yield engine
    await engine.dispose()


def create_async_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def make_alembic_config(cmd_opts: Namespace, base_path: Path = PROJECT_PATH) -> Config:
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = str(base_path / "lms/db" / cmd_opts.config)

    config = Config(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,
    )

    alembic_location = config.get_main_option("script_location")
    if not alembic_location:
        raise ValueError
    if not os.path.isabs(alembic_location):
        config.set_main_option("script_location", str(base_path / alembic_location))

    if cmd_opts.pg_dsn:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_dsn)

    config.attributes["configure_logger"] = False

    return config


def make_pg_enum(enum_cls: type[StrEnum], **kwargs: Any) -> pg.ENUM:
    return pg.ENUM(
        enum_cls,
        values_callable=_choices,
        **kwargs,
    )


def _choices(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    return tuple(map(str, enum_cls))
