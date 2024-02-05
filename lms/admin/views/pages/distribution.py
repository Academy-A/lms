import logging
from collections.abc import Sequence
from datetime import datetime
from http import HTTPMethod, HTTPStatus
from json import JSONDecodeError
from types import MappingProxyType
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from yarl import URL

from lms.admin.exceptions import ExtendedHTTPException
from lms.admin.views.pages.base import BaseCustomView
from lms.db.repositories.product import ProductRepository
from lms.generals.models.product import Product
from lms.utils.distribution.models import DistributionParams
from lms.utils.http import create_web_session

log = logging.getLogger(__name__)


async def bad_request(
    exc: ExtendedHTTPException,
    request: Request,
    templates: Jinja2Templates,
    template_path: str,
) -> Response:
    return templates.TemplateResponse(
        template_path,
        {
            "request": request,
            "errors": exc.errors(),
        },
    )


class DistributionView(BaseCustomView):
    ERROR_HANDLERS = MappingProxyType(
        {
            HTTPStatus.BAD_REQUEST: bad_request,
        }
    )

    async def _render(
        self,
        request: Request,
        templates: Jinja2Templates,
    ) -> Response:
        result = {}
        errors: list[Any] = []
        try:
            if request.method == HTTPMethod.POST:
                params = await self._parse_params(request=request)
                await self._call_create_distribution(params=params)
                result["msg"] = "Distribution was created!"
        except ExtendedHTTPException as e:
            log.info("Form not parsed")
            errors.extend(e.errors())

        products = await self._get_product_list(request=request)
        return templates.TemplateResponse(
            self.template_path,
            {
                "request": request,
                "products": products,
                "result": result,
                "errors": errors,
            },
        )

    async def _get_product_list(self, request: Request) -> Sequence[Product]:
        session: AsyncSession = request.state.session
        now = datetime.now()
        return await ProductRepository(session=session).read_actual_list(dt=now)

    async def _parse_params(
        self,
        request: Request,
    ) -> DistributionParams:
        form = await request.form()
        try:
            return DistributionParams.parse_form(form)
        except ValidationError as err:
            raise ExtendedHTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                errors=err.errors(),
            )
        except JSONDecodeError:
            raise ExtendedHTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                errors=[
                    {
                        "msg": "Cannot parse JSON object",
                        "loc": "body",
                    },
                ],
            )

    async def _call_create_distribution(self, params: DistributionParams) -> None:
        url = URL("http://0.0.0.0:80/v1/products/distribute").with_query(
            dict(token=self.token)
        )
        async with create_web_session(raise_for_status=False) as session:
            async with session.post(
                url, json=params.model_dump(mode="json")
            ) as response:
                a = await response.text()
                log.info("response: %s ", a)
