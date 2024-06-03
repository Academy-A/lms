import pytest

from lms.rest.args import Parser


@pytest.fixture
def parser(
    api_secret_key: str,
    localhost: str,
    rest_port: int,
    pg_dsn: str,
    soho_api_token: str,
    telegram_bot_token: str,
    telegram_chat_id: int,
    google_keys_encoded: str,
) -> Parser:
    parser = Parser()
    return parser.parse_args(
        [
            "--log-level=debug",
            "--log-format=color",
            "--pool-size=6",
            f"--api-host={localhost}",
            f"--api-port={rest_port}",
            f"--api-secret-key={api_secret_key}",
            f"--pg-dsn={pg_dsn}",
            f"--soho-api-token={soho_api_token}",
            f"--telegram-bot-token={telegram_bot_token}",
            f"--telegram-chat-id={telegram_chat_id}",
            "--telegram-parse-mode=markdown",
            f"--google-keys={google_keys_encoded}",
        ],
    )
