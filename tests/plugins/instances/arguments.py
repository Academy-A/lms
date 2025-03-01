import pytest

from lms.adapters.db.config import DatabaseConfig
from lms.adapters.google.config import GoogleConfig
from lms.adapters.soho.config import SohoConfig
from lms.adapters.telegram.config import TelegramConfig
from lms.application.http import HttpConfig
from lms.application.security import SecurityConfig
from lms.presentation.rest.config import Config


@pytest.fixture
def config(
    api_secret_key: str,
    localhost: str,
    rest_port: int,
    pg_dsn: str,
    soho_api_token: str,
    telegram_bot_token: str,
    telegram_chat_id: int,
    google_keys_encoded: str,
) -> Config:
    return Config(
        security=SecurityConfig(secret_key=api_secret_key),
        http=HttpConfig(
            host=localhost,
            port=rest_port,
        ),
        db=DatabaseConfig(dsn=pg_dsn),
        soho=SohoConfig(token=soho_api_token),
        telegram=TelegramConfig(
            bot_token=telegram_bot_token,
            chat_id=telegram_chat_id,
        ),
        google=GoogleConfig(keys=google_keys_encoded),
    )
