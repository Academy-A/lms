from dataclasses import dataclass, field

from lms.adapters.db.config import DatabaseConfig
from lms.adapters.google.config import GoogleConfig
from lms.adapters.soho.config import SohoConfig
from lms.adapters.telegram.config import TelegramConfig
from lms.application.config import AppConfig
from lms.application.http import HttpConfig
from lms.application.logging import LoggingConfig
from lms.application.security import SecurityConfig


@dataclass(frozen=True, slots=True, kw_only=True)
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    log: LoggingConfig = field(default_factory=LoggingConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    soho: SohoConfig = field(default_factory=SohoConfig)
    google: GoogleConfig = field(default_factory=GoogleConfig)
    http: HttpConfig = field(default_factory=HttpConfig)
