import logging
from collections.abc import Awaitable, Callable, Mapping
from functools import cached_property
from http import HTTPStatus
from types import MappingProxyType
from typing import Any

from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from lms.admin.exceptions import ExtendedHTTPException
from lms.rest.api.auth import generate_token

log = logging.getLogger(__name__)

ErrorHandlersType = Mapping[
    HTTPStatus | int | str,
    Callable[[ExtendedHTTPException, Request, Jinja2Templates, str], Awaitable],
]


class BaseCustomView(CustomView):
    ERROR_HANDLERS: ErrorHandlersType

    def __init__(
        self,
        label: str,
        icon: str | None = None,
        path: str = "/",
        template_path: str = "index.html",
        name: str | None = None,
        methods: list[str] | None = None,
        add_to_menu: bool = True,
        **kwargs: Any,
    ):
        super().__init__(label, icon, path, template_path, name, methods, add_to_menu)
        self._deps = MappingProxyType(kwargs)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        try:
            return await self._render(request=request, templates=templates)
        except ExtendedHTTPException as e:
            func = self.ERROR_HANDLERS.get(e.status_code)
            if func is None:
                log.error("Unhandled http status")
                raise
            return await func(e, request, templates, self.template_path)

    async def _render(self, request: Request, templates: Jinja2Templates) -> Response:
        return await super().render(request=request, templates=templates)

    @cached_property
    def token(self) -> str:
        return generate_token({"source": "admin"}, self._deps["secret_key"])
