from datetime import datetime
from http import HTTPStatus
from types import MappingProxyType
from typing import ClassVar

from aiohttp import ClientSession, hdrs
from pydantic import BaseModel, Field, HttpUrl
from yarl import URL

from lms.clients.base.client import BaseHttpClient
from lms.clients.base.handlers import parse_model
from lms.clients.base.root_handler import ResponseHandlersType
from lms.clients.base.timeout import TimeoutType


class SohoHomework(BaseModel):
    student_homework_id: int = Field(alias="clientHomeworkId")
    student_soho_id: int = Field(alias="clientId")
    sent_to_review_at: datetime = Field(alias="sentToReviewAt")
    chat_url: HttpUrl = Field(alias="chatUrl")
    student_vk_id: int | None = Field(alias="vkId", default=None)


class SohoHomeworksResponse(BaseModel):
    homeworks: list[SohoHomework]


class ClientSchema(BaseModel):
    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName", default="")
    emails: list[str]


class SohoClientListSchema(BaseModel):
    clients: list[ClientSchema]
    limit: int
    offset: int


class PaymentSchema(BaseModel):
    id: int
    name: str
    percent: int


class SohoProductSchema(BaseModel):
    id: int = Field(alias="productId")
    flow_id: int | None = Field(alias="flowId", default=None)
    name: str
    payment_schemas: list[PaymentSchema] = Field(alias="paymentSchemas")


class SohoProductListSchema(BaseModel):
    products: SohoProductSchema


SOHO_BASE_URL = URL("https://api.soholms.com")


class Soho(BaseHttpClient):
    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = 2

    HOMEWORKS_FOR_REVIEW_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: parse_model(SohoHomeworksResponse),
        }
    )
    PRODUCT_LIST_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: parse_model(SohoProductListSchema),
        }
    )
    CLIENT_LIST_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: parse_model(SohoClientListSchema),
        }
    )

    def __init__(
        self,
        url: URL,
        session: ClientSession,
        auth_token: str,
        client_name: str | None = None,
    ):
        super().__init__(url, session, client_name)
        self._auth_header = {"Authorization": auth_token}

    async def homeworks(
        self,
        homework_id: int,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> SohoHomeworksResponse:
        return await self._make_req(
            method=hdrs.METH_POST,
            url=self._url / "api/v1/learning/homework/for_review_list",
            headers=self._auth_header,
            handlers=self.HOMEWORKS_FOR_REVIEW_HANDLERS,
            timeout=timeout,
            json={
                "homeworkId": homework_id,
            },
        )

    async def client_list(
        self,
        offset: int = 0,
        limit: int = 100,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> SohoClientListSchema:
        return await self._make_req(
            method=hdrs.METH_POST,
            url=self._url / "api/v1/client/find_clients",
            headers=self._auth_header,
            handlers=self.CLIENT_LIST_HANDLERS,
            timeout=timeout,
            json={
                "limit": limit,
                "offset": offset,
            },
        )

    async def product_list(
        self,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> SohoProductListSchema:
        return await self._make_req(
            method=hdrs.METH_POST,
            url=self._url / "api/v1/product/list",
            headers=self._auth_header,
            handlers=self.PRODUCT_LIST_HANDLERS,
            timeout=timeout,
        )
