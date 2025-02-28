from collections.abc import Mapping
from http import HTTPStatus
from types import MappingProxyType
from typing import Any, ClassVar

from aiohttp import ClientSession, hdrs
from aiomisc import asyncbackoff
from pydantic import BaseModel, Field
from yarl import URL

from lms.clients.base.client import BaseHttpClient
from lms.clients.base.handlers import parse_model
from lms.clients.base.root_handler import ResponseHandlersType
from lms.clients.base.timeout import TimeoutType

TELEGRAM_BASE_URL = URL("https://api.telegram.org")


class TelegramSendMessageFrom(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: str


class TelegramSendMessageChat(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str
    type: str


class TelegramSendMessageResult(BaseModel):
    message_id: int
    from_: TelegramSendMessageFrom = Field(alias="from")
    chat: TelegramSendMessageChat
    date: int
    text: str


class TelegramSendMessageSchema(BaseModel):
    ok: bool
    result: TelegramSendMessageResult


class Telegram(BaseHttpClient):
    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = 2
    SEND_MESSAGE_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: parse_model(TelegramSendMessageSchema),
        }
    )

    _bot_token: str
    _default_chat_id: int
    _default_parse_mode: str

    def __init__(
        self,
        bot_token: str,
        default_chat_id: int,
        default_parse_mode: str,
        url: URL,
        session: ClientSession,
        client_name: str | None = None,
    ):
        super().__init__(url=url, session=session, client_name=client_name)
        self._bot_token = bot_token
        self._default_chat_id = default_chat_id
        self._default_parse_mode = default_parse_mode

    async def teacher_overflow_alert(
        self, name: str, max_students: int, vk_id: int, product_id: int
    ) -> None:
        text = (
            f"Teacher {name} with VK ID {vk_id} was overflow "
            "limit {max_students} on product {product_id}"
        )
        data = {
            "chat_id": self._default_chat_id,
            "parse_mode": self._default_parse_mode,
            "text": text,
        }
        return await self.send_message(data=data)

    @asyncbackoff(attempt_timeout=1, max_tries=3, pause=0.1, deadline=5)
    async def send_message(
        self,
        data: Mapping[str, Any],
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> TelegramSendMessageSchema:
        return await self._make_req(
            method=hdrs.METH_POST,
            url=self._url / f"bot{self._bot_token}/sendMessage",
            handlers=self.SEND_MESSAGE_HANDLERS,
            timeout=timeout,
            data=data,
        )
