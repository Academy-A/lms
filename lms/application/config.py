from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, slots=True, kw_only=True)
class AppConfig:
    debug: bool = field(
        default_factory=lambda: environ.get("APP_DEBUG", "false").lower() == "true"
    )
    pool_size: int = field(
        default_factory=lambda: int(environ.get("APP_POOL_SIZE", "4"))
    )
