from argparse import Namespace

import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_app import Application
from aiomisc_log import LogFormat, LogLevel
from sqlalchemy.ext.asyncio import AsyncEngine
from yarl import URL

from lms.clients.autopilot import Autopilot
from lms.clients.soho import Soho
from lms.clients.telegram import Telegram
from lms.rest.api.auth import generate_token
from lms.rest.service import REST


@pytest.fixture
def api_secret_key() -> str:
    return "api-super-secret"


@pytest.fixture
def rest_port(aiomisc_unused_port_factory) -> int:
    return aiomisc_unused_port_factory()


@pytest.fixture
def rest_service(
    args: Namespace,
    async_engine: AsyncEngine,
    autopilot: Autopilot,
    soho: Soho,
    telegram: Telegram,
    sessionmaker,
    get_distributor,
) -> REST:
    return REST(
        debug=args.debug,
        project_name=args.project_name,
        project_description=args.project_description,
        project_version=args.project_version,
        secret_key=args.api_secret_key,
        address=args.api_address,
        port=args.api_port,
        engine=async_engine,
        autopilot=autopilot,
        soho=soho,
        telegram=telegram,
        session_factory=sessionmaker,
        get_distributor=get_distributor,
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
