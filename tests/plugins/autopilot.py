import pytest
from yarl import URL

from lms.clients.autopilot import Autopilot
from lms.utils.http import create_web_session
from tests.utils.srvmocker.models import MockService
from tests.utils.srvmocker.service import start_service


@pytest.fixture
async def autopilot_service(localhost):
    routes = []
    async with start_service(localhost, routes) as service:
        yield service


@pytest.fixture
def autopilot_url(autopilot_service: MockService) -> URL:
    return autopilot_service.url


@pytest.fixture
async def autopilot(autopilot_url: URL) -> Autopilot:
    async with create_web_session() as session:
        yield Autopilot(
            url=autopilot_url,
            session=session,
        )
