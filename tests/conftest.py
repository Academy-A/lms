import os
from argparse import Namespace
from collections.abc import AsyncGenerator
from pathlib import Path
from types import SimpleNamespace

import pytest
from aiohttp.test_utils import TestClient, TestServer
from alembic.config import Config as AlembicConfig
from pydantic import PostgresDsn
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from yarl import URL

from lms.api.auth import generate_token
from lms.api.service import REST
from lms.arguments import parser
from lms.clients.telegram import TelegramClient
from lms.db.models import Base
from lms.db.uow import UnitOfWork
from lms.db.utils import make_alembic_config
from lms.deps import configure_dependencies
from tests.factories import factories
from tests.utils import clear_db, prepare_new_database, run_async_migrations


def make_pg_dsn(from_dsn: PostgresDsn, database: str) -> str:
    parsed_url = make_url(str(from_dsn))
    new_url = parsed_url.set(database=database)

    return new_url.render_as_string(hide_password=False)


@pytest.fixture
def project_path() -> Path:
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def database() -> str:
    return "test_lms_db"


@pytest.fixture
def pg_dsn(database: str) -> str:
    app_pg_dsn = PostgresDsn(os.environ.get("APP_PG_DSN"))
    return str(make_pg_dsn(app_pg_dsn, database))


@pytest.fixture
def base_pg_dsn() -> str:
    app_pg_dsn = PostgresDsn(os.environ.get("APP_PG_DSN"))
    return str(make_pg_dsn(app_pg_dsn, "postgres"))


@pytest.fixture
def rest_port(aiomisc_unused_port_factory) -> int:
    return aiomisc_unused_port_factory()


@pytest.fixture
def stairway_db() -> str:
    return "stairway"


@pytest.fixture
def telegram_client(arguments) -> TelegramClient:
    return TelegramClient(
        bot_token=arguments.telegram_bot_token,
        default_chat_id=arguments.telegram_chat_id,
        default_parse_mode=arguments.telegram_parse_mode,
    )


@pytest.fixture
def api_service(
    arguments, async_engine, telegram_client: TelegramClient, uow: UnitOfWork
) -> REST:
    return REST(
        debug=False,
        project_name=arguments.project_name,
        project_description=arguments.project_description,
        project_version=arguments.project_version,
        secret_key=arguments.api_secret_key,
        address=arguments.api_address,
        port=arguments.api_port,
        engine=async_engine,
        telegram_client=telegram_client,
        uow=uow,
    )


@pytest.fixture
def arguments(
    localhost,
    rest_port,
    pg_dsn: str,
) -> Namespace:
    args = parser.parse_args(
        [
            "--soho-api-token=test_soho_token",
            "--api-secret-key=test_secret_key",
            f"--pg-dsn={pg_dsn}",
            "--telegram-bot-token=test_telegram_bot_token",
            "--chat-id=0",
            f"--api-address={localhost}",
            f"--api-port={rest_port}",
        ]
    )
    configure_dependencies(args)
    return args


@pytest.fixture
def alembic_config(pg_dsn: str) -> AlembicConfig:
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_dsn=pg_dsn,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


@pytest.fixture
async def async_engine(
    base_pg_dsn: str,
    pg_dsn: str,
    database: str,
    alembic_config: AlembicConfig,
    stairway_db: str,
):
    print(pg_dsn)
    print(base_pg_dsn)
    await prepare_new_database(base_pg_dsn=base_pg_dsn, new_database=database)
    await prepare_new_database(base_pg_dsn=base_pg_dsn, new_database=stairway_db)
    await run_async_migrations(alembic_config, Base.metadata, "head")
    engine = create_async_engine(pg_dsn)
    yield engine
    await engine.dispose()


@pytest.fixture
async def sessionmaker(async_engine: AsyncEngine):
    yield async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture(autouse=True, scope="function")
async def session(
    sessionmaker: async_sessionmaker[AsyncSession],
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        for factory in factories:
            factory.__async_session__ = session
        yield session
    await clear_db(async_engine)


@pytest.fixture()
async def uow(sessionmaker) -> UnitOfWork:
    return UnitOfWork(sessionmaker)


@pytest.fixture
async def http_client(loop, api_service, arguments: Namespace):
    server = TestServer(api_service)
    server._root = URL.build(
        scheme="http",
        host=arguments.api_address,
        port=arguments.api_port,
    )
    client = TestClient(server)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
def entrypoint_kwargs(arguments: Namespace) -> dict:
    return {
        "log_format": arguments.log_format,
        "log_level": arguments.log_level,
    }


@pytest.fixture
def token(arguments) -> str:
    return generate_token(
        data={"test_data": True},
        secret_key=arguments.api_secret_key,
    )
