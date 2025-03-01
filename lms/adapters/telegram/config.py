from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, kw_only=True, slots=True)
class TelegramConfig:
    bot_token: str = field(default_factory=lambda: environ["APP_TELEGRAM_BOT_TOKEN"])
    chat_id: int = field(default_factory=lambda: int(environ["APP_TELEGRAM_CHAT_ID"]))
    parse_mode: str = field(
        default_factory=lambda: environ.get("APP_TELEGRAM_PARSE_MODE", "markdown")
    )
