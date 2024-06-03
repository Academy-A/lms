import base64
import logging

import argclass
import orjson
from aiomisc_log import LogFormat, LogLevel
from google_api_service_helper import GoogleKeys

log = logging.getLogger(__name__)


def load_google_keys(v: str) -> GoogleKeys:
    try:
        json_str = base64.b64decode(v)
        data = orjson.loads(json_str)
        return GoogleKeys(**data)
    except ValueError:
        log.warning("Can not load google keys")
        raise


class LogGroup(argclass.Group):
    level: LogLevel = argclass.EnumArgument(LogLevel, default=LogLevel.info)
    format: LogFormat = argclass.EnumArgument(LogFormat, default=LogFormat.color)


class DatabaseGroup(argclass.Group):
    pg_dsn: str = argclass.Argument("--pg-dsn", required=True, type=str)


class APIGroup(argclass.Group):
    host: str = argclass.Argument("--api-host", default="127.0.0.1")
    port: int = argclass.Argument("--api-port", type=int, default=8000)
    title: str = argclass.Argument("--api-title", default="LMS")
    description: str = argclass.Argument("--api-description", default="LMS API")
    version: str = argclass.Argument("--api-version", default="1.0.1")


class SecurityGroup(argclass.Group):
    secret_key: str = argclass.Argument("--api-secret-key", required=True, type=str)


class CronGroup(argclass.Group):
    scheduler: str = argclass.Argument("--scheduler", default="0/30 * * * *")


class TelegramGroup(argclass.Group):
    bot_token: str = argclass.Argument("--telegram-bot-token", type=str, required=True)
    chat_id: int = argclass.Argument("--telegram-chat-id", type=int, required=True)
    parse_mode: str = argclass.Argument(
        "--telegram-parse-mode", type=str, default="markdown"
    )


class SohoGroup(argclass.Group):
    token: str = argclass.Argument("--soho-api-token", type=str, required=True)


class GoogleGroup(argclass.Group):
    keys: GoogleKeys = argclass.Argument(
        "--google-keys", required=True, type=load_google_keys
    )


class AutopilotGroup(argclass.Group):
    regular_notification_url: str = argclass.Argument(
        "--regular-notification-url", required=True, type=str
    )
    subscription_notification_url: str = argclass.Argument(
        "--subscription-notification-url", required=True, type=str
    )
    additional_notification_url: str = argclass.Argument(
        "--additional-notification-url", required=True, type=str
    )
