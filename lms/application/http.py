from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, kw_only=True, slots=True)
class HttpConfig:
    host: str = field(default_factory=lambda: environ.get("APP_HTTP_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(environ.get("APP_HTTP_PORT", "8000")))
    title: str = field(default_factory=lambda: environ.get("APP_HTTP_TITLE", "LMS"))
    description: str = field(
        default_factory=lambda: environ.get("APP_HTTP_DESCRIPTION", "LMS API")
    )
    version: str = field(
        default_factory=lambda: environ.get("APP_HTTP_VERSION", "1.0.1")
    )
