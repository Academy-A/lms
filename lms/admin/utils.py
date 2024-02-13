from collections.abc import Callable

from pyparsing import Any
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette_admin import DateTimeField

CREATED_AT_FIELD = DateTimeField(
    name="created_at",
    label="Created at",
    output_format="%H:%M:%S %d.%m.%Y",
    exclude_from_list=True,
    required=True,
    form_alt_format="H:i:S d.m.Y",
)
UPDATED_AT_FIELD = DateTimeField(
    name="updated_at",
    label="Updated at",
    output_format="%H:%M:%S %d.%m.%Y",
    exclude_from_list=True,
    required=True,
    form_alt_format="H:i:S d.m.Y",
)


def template_cache_key_builder(
    func: Callable, obj: Any, request: Request, templates: Jinja2Templates
) -> str:
    return str(obj) + func.__name__ + str(templates)
