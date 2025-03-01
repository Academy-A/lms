from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, slots=True, kw_only=True)
class DatabaseConfig:
    dsn: str = field(default_factory=lambda: environ["APP_DATABASE_DSN"])
