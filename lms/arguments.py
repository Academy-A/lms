import argparse
import logging

import configargparse
import orjson
from aiomisc_log import LogFormat, LogLevel
from google_api_service_helper import GoogleKeys

log = logging.getLogger(__name__)


def load_google_keys(v: str) -> GoogleKeys:
    try:
        with open(v, "rb") as f:
            data = orjson.loads(f.read())
        return GoogleKeys(**data)
    except ValueError:
        log.warning("Can not load google keys")
        raise


parser = configargparse.ArgumentParser(
    allow_abbrev=False,
    auto_env_var_prefix="APP_",
    description="Project LMS",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument("-D", "--debug", action="store_true")
parser.add_argument(
    "-s",
    "--pool-size",
    type=int,
    default=6,
    help="Thread pool size",
)

group = parser.add_argument_group("Logging options")
group.add_argument("--log-level", default=LogLevel.info, choices=LogLevel.choices())
group.add_argument("--log-format", choices=LogFormat.choices(), default=LogFormat.color)

group = parser.add_argument_group("Project options")
group.add_argument("--project-name", default="LMS")
group.add_argument("--project-description", default="LMS API")
group.add_argument("--project-version", default="1.0.1")

group = parser.add_argument_group("API options")
group.add_argument("--api-address", default="127.0.0.1")
group.add_argument("--api-port", type=int, default=8000)
group.add_argument("--api-secret-key", required=True, type=str)

group = parser.add_argument_group("PostgreSQL options")
group.add_argument("--pg-dsn", required=True, type=str)

group = parser.add_argument_group("Cron options")
group.add_argument("--scheduler", default="0/30 * * * *")

group = parser.add_argument_group("SOHO options")
group.add_argument("--soho-api-token", type=str, required=True)

group = parser.add_argument_group("Telegram options")
group.add_argument("--telegram-bot-token", type=str, required=True)
group.add_argument("--telegram-chat-id", type=int, required=True)
group.add_argument("--telegram-parse-mode", type=str, default="markdown")

group = parser.add_argument_group("Google Keys")
group.add_argument("--google-keys", required=True, type=load_google_keys)
