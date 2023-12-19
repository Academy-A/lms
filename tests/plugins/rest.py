import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_app import Application
from aiomisc_log import LogFormat, LogLevel
from yarl import URL

from lms.api.auth import generate_token
from lms.api.service import REST
from lms.clients.autopilot import Autopilot
from lms.clients.soho import Soho
from lms.clients.telegram import Telegram
from lms.db.uow import UnitOfWork


@pytest.fixture
def app_secret_key() -> str:
    return "api-super-secret"


@pytest.fixture
def rest_port(aiomisc_unused_port_factory) -> int:
    return aiomisc_unused_port_factory()


@pytest.fixture
def rest_service(
    async_engine,
    autopilot: Autopilot,
    soho: Soho,
    telegram: Telegram,
    uow: UnitOfWork,
    app_secret_key: str,
    rest_port: int,
    localhost,
    sessionmaker,
) -> REST:
    return REST(
        debug=False,
        project_name="Test LMS",
        project_description="test lms description",
        project_version="0.0.1",
        secret_key=app_secret_key,
        address=localhost,
        port=rest_port,
        engine=async_engine,
        autopilot=autopilot,
        soho=soho,
        telegram=telegram,
        uow=uow,
        session_factory=sessionmaker,
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
def token(app_secret_key: str) -> str:
    return generate_token(
        data={"test_data": True},
        secret_key=app_secret_key,
    )
