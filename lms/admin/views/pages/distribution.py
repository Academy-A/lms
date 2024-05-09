import logging
from collections.abc import Sequence
from datetime import datetime
from functools import cached_property
from http import HTTPMethod

from pydantic import ValidationError
from sqladmin import BaseView, expose
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import Response
from yarl import URL

from lms.db.repositories.product import ProductRepository
from lms.generals.models.product import Product
from lms.rest.api.auth import generate_token
from lms.utils.distribution.models import DistributionParams
from lms.utils.http import create_web_session

log = logging.getLogger(__name__)


class DistributionView(BaseView):
    secret_key: str
    session_factory: async_sessionmaker[AsyncSession]

    name = "Distribution"

    @expose(path="/create-distribution", methods=[HTTPMethod.GET, HTTPMethod.POST])
    async def create_distribution(self, request: Request) -> Response:
        result = {}
        errors = []
        if request.method == HTTPMethod.POST:
            form_data = await request.form()
            try:
                params = DistributionParams.parse_form(form_data)
                await self._call_create_distribution(params=params)
                result["msg"] = "Distribution was created!"
            except ValidationError as e:
                log.info("Form not parsed")
                errors = e.errors()

        products = await self._get_product_list()
        return await self.templates.TemplateResponse(
            request=request,
            name="./distribution.html",
            context={
                "products": products,
                "result": result,
                "errors": errors,
                "title": "Распределение домашних работ",
            },
        )

    async def _call_create_distribution(self, params: DistributionParams) -> None:
        url = URL("http://0.0.0.0:80/v1/products/distribute/").with_query(
            dict(token=self.token)
        )
        async with create_web_session(raise_for_status=False) as session:
            async with session.post(
                url, json=params.model_dump(mode="json")
            ) as response:
                a = await response.text()
                log.info("response: %s ", a)

    async def _get_product_list(self) -> Sequence[Product]:
        async with self.session_factory() as session:
            now = datetime.now()
            return await ProductRepository(session=session).get_actual_list(dt=now)

    @cached_property
    def token(self) -> str:
        return generate_token({"source": "admin"}, self.secret_key)
