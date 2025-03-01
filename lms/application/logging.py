from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from os import environ
from typing import TypeVar

from aiomisc_log import LogFormat, LogLevel

T = TypeVar("T", bound=Enum)


def enum_parser(enum: type[T], default: T) -> Callable[[str], T]:
    def parser(val: str) -> T:
        try:
            return enum.__members__[val.lower()]
        except KeyError:
            return default

    return parser


def get_log_level() -> LogLevel:
    val = environ.get("APP_LOG_LEVEL", "info")
    return enum_parser(LogLevel, LogLevel.info)(val)


def get_log_format() -> LogFormat:
    val = environ.get("APP_LOG_FORMAT", "color")
    return enum_parser(LogFormat, LogFormat.color)(val)


@dataclass(frozen=True, kw_only=True, slots=True)
class LoggingConfig:
    level: LogLevel = field(default_factory=get_log_level)
    format: LogFormat = field(default_factory=get_log_format)
