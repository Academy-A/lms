import pytest
from yarl import URL

from lms.adapters.soho.soho import Soho
from lms.utils.http import create_web_session
from tests.utils.srvmocker.models import MockRoute, MockService
from tests.utils.srvmocker.responses import JsonResponse
from tests.utils.srvmocker.service import start_service


@pytest.fixture
def soho_api_token() -> str:
    return "soho_api_token"


@pytest.fixture
async def soho_service(localhost: str):
    routes = [
        MockRoute("POST", "/api/v1/learning/homework/for_review_list", "homeworks"),
        MockRoute("POST", "/api/v1/client/find_clients", "client_list"),
        MockRoute("POST", "/api/v1/product/list", "product_list"),
    ]
    async with start_service(localhost, routes) as service:
        service.register("homeworks", JsonResponse())
        service.register("client_list", JsonResponse())
        service.register("product_list", JsonResponse())
        yield service


@pytest.fixture
def soho_url(soho_service: MockService) -> URL:
    return soho_service.url


@pytest.fixture
async def soho(
    soho_url: URL,
    soho_api_token: str,
):
    async with create_web_session() as session:
        yield Soho(
            url=soho_url,
            session=session,
            auth_token=soho_api_token,
            client_name="soho",
        )
