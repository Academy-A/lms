import asyncio
from datetime import datetime
from http import HTTPStatus
from types import MappingProxyType
from typing import ClassVar

from aiohttp import ClientSession
from aiomisc import asyncretry
from asyncly import BaseHttpClient, ResponseHandlersType, TimeoutType
from asyncly.client.handlers.pydantic import parse_model
from pydantic import BaseModel, Field
from yarl import URL


class SohoHomeworkResponse(BaseModel):
    student_homework_id: int = Field(alias="clientHomeworkId")
    student_soho_id: int = Field(alias="clientId")
    sent_to_review_at: datetime = Field(alias="sentToReviewAt")
    chat_url: str = Field(alias="chatUrl")
    student_vk_id: int | None = Field(alias="vkId", default=None)


class SohoHomeworksResponse(BaseModel):
    homeworks: list[SohoHomeworkResponse]


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
    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = 30

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
        client_name: str,
    ):
        super().__init__(url, session, client_name)
        self._auth_header = {"Authorization": auth_token}

    async def homeworks(
        self,
        homework_id: int,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> SohoHomeworksResponse:
        return await self._make_req(
            method="POST",
            url=self._url / "api/v1/learning/homework/for_review_list",
            headers=self._auth_header,
            handlers=self.HOMEWORKS_FOR_REVIEW_HANDLERS,
            timeout=timeout,
            json={
                "homeworkId": homework_id,
            },
        )

    async def fetch_all_clients(self) -> list[ClientSchema]:
        clients = []
        offset = 0
        while True:
            response = await self.client_list(offset=offset)
            clients.extend(response.clients)
            if len(response.clients) < response.limit:
                break
            offset += len(response.clients)
            await asyncio.sleep(0.5)
        return clients

    @asyncretry(max_tries=5, pause=1)
    async def client_list(
        self,
        offset: int = 0,
        limit: int = 100,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> SohoClientListSchema:
        return await self._make_req(
            method="POST",
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
            method="POST",
            url=self._url / "api/v1/product/list",
            headers=self._auth_header,
            handlers=self.PRODUCT_LIST_HANDLERS,
            timeout=timeout,
        )
