import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_app import Application
from aiomisc_log import LogFormat, LogLevel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from yarl import URL

from lms.adapters.db.uow import UnitOfWork
from lms.clients.autopilot import Autopilot
from lms.clients.soho import Soho
from lms.clients.telegram import Telegram
from lms.logic.enroll_student import Enroller
from lms.presentation.rest.api.auth import generate_token
from lms.presentation.rest.config import Config
from lms.presentation.rest.service import REST


@pytest.fixture
def api_secret_key() -> str:
    return "api-super-secret"


@pytest.fixture
def rest_port(aiomisc_unused_port_factory) -> int:
    return aiomisc_unused_port_factory()


@pytest.fixture
def enroller(
    sessionmaker: async_sessionmaker[AsyncSession],
    autopilot: Autopilot,
    telegram: Telegram,
) -> Enroller:
    return Enroller(
        uow=UnitOfWork(sessionmaker=sessionmaker),
        autopilot=autopilot,
        telegram=telegram,
    )


@pytest.fixture
def rest_service(
    config: Config,
    engine: AsyncEngine,
    autopilot: Autopilot,
    soho: Soho,
    telegram: Telegram,
    enroller: Enroller,
    sessionmaker: async_sessionmaker[AsyncSession],
    get_distributor,
) -> REST:
    return REST(
        debug=config.app.debug,
        title=config.http.title,
        description=config.http.description,
        version=config.http.version,
        secret_key=config.security.secret_key,
        host=config.http.host,
        port=config.http.port,
        engine=engine,
        autopilot=autopilot,
        soho=soho,
        telegram=telegram,
        session_factory=sessionmaker,
        get_distributor=get_distributor,
        enroller=enroller,
    )


@pytest.fixture
def services(rest_service: REST):
    return [rest_service]


@pytest.fixture
async def api_client(localhost, rest_port, rest_service):
    server = TestServer(Application())
    server._root = URL.build(
        scheme="http",
        host=localhost,
        port=rest_port,
    )
    client = TestClient(server)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
def entrypoint_kwargs() -> dict[str, str]:
    return {
        "log_format": LogFormat.color,
        "log_level": LogLevel.info,
    }


@pytest.fixture
def token(api_secret_key: str) -> str:
    return generate_token(
        data={"test_data": True},
        secret_key=api_secret_key,
    )
