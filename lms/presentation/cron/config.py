from dataclasses import dataclass, field
from os import environ

from lms.adapters.autopilot.config import AutopilotConfig
from lms.adapters.db.config import DatabaseConfig
from lms.adapters.google.config import GoogleConfig
from lms.application.config import AppConfig
from lms.application.logging import LoggingConfig


@dataclass(frozen=True, kw_only=True, slots=True)
class CronConfig:
    scheduler: str = field(
        default_factory=lambda: environ.get("APP_CRON_SCHEDULER", "0/30 * * * *")
    )


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    log: LoggingConfig = field(default_factory=LoggingConfig)
    cron: CronConfig = field(default_factory=CronConfig)
    autopilot: AutopilotConfig = field(default_factory=AutopilotConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    google: GoogleConfig = field(default_factory=GoogleConfig)
