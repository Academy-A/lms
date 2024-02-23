from collections.abc import Callable, Mapping
from datetime import date, datetime

from pyparsing import Any
from sqlalchemy import Column
from starlette.requests import Request


def template_cache_key_builder(func: Callable, obj: Any, request: Request) -> str:
    return str(obj) + func.__name__


def exlude_property_field(field: str) -> Callable:
    def property_field(obj: type, attr: Column) -> str:
        properties: Mapping[str, Any] | None = getattr(obj, "properties", None)
        if properties is None:
            return ""
        return properties.get(field, "")

    return property_field


def format_datetime_field(obj: type, attr: Column) -> str:
    value: datetime | None = getattr(obj, str(attr))
    if value is None:
        return ""
    return value.strftime("%H:%M:%S %d.%m.%Y")


def format_date_field(obj: type, attr: Column) -> str:
    value: date | None = getattr(obj, str(attr))
    if value is None:
        return ""
    return value.strftime("%d.%m.%Y")


def format_float_field(ndigits: int) -> Callable:
    def _format(obj: type, attr: Column) -> str:
        value: float | None = getattr(obj, str(attr))
        if value is None:
            return ""
        return str(round(value, ndigits=ndigits))

    return _format


def format_vk_id_field(obj: type, attr: Column) -> str:
    value: int | None = getattr(obj, str(attr))
    if value is None:
        return ""
    return f"https://vk.com/id{value}"


def format_max_length(char_count: int) -> Callable:
    def _format(obj: type, attr: Column) -> str:
        value: str | None = getattr(obj, str(attr))
        if value is None:
            return ""
        return value[:char_count] + "..."

    return _format
