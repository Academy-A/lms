import pytest
from yarl import URL

from lms.clients.telegram import Telegram
from lms.utils.http import create_web_session
from tests.utils.srvmocker import JsonResponse, MockRoute, MockService, start_service


@pytest.fixture
def telegram_bot_token() -> str:
    return "test_token"


@pytest.fixture
def telegram_chat_id() -> int:
    return 0


@pytest.fixture
def telegram_parse_mode() -> str:
    return "markdown"


@pytest.fixture
async def telegram_service(localhost, telegram_bot_token: str):
    routes = [
        MockRoute("POST", f"/bot{telegram_bot_token}/sendMessage", "send_message"),
    ]
    async with start_service(localhost, routes) as service:
        service.register("send_message", JsonResponse())
        yield service


@pytest.fixture
def telegram_url(telegram_service: MockService) -> URL:
    return telegram_service.url


@pytest.fixture
async def telegram(
    telegram_url: URL,
    telegram_bot_token: str,
    telegram_chat_id: int,
    telegram_parse_mode: str,
) -> Telegram:
    async with create_web_session() as session:
        yield Telegram(
            url=telegram_url,
            session=session,
            bot_token=telegram_bot_token,
            default_chat_id=telegram_chat_id,
            default_parse_mode=telegram_parse_mode,
        )
