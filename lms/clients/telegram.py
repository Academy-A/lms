from typing import Any

import aiohttp
from aiomisc import asyncbackoff
from pydantic import SecretStr
from yarl import URL

BASE_URL = URL("https://api.telegram.org")


class TelegramClient:
    def __init__(
        self, bot_token: SecretStr, default_chat_id: int, default_parse_mode: str
    ) -> None:
        self._bot_token = bot_token
        self._default_chat_id = default_chat_id
        self._default_parse_mode = default_parse_mode

    async def send_teacher_overflow_alert(
        self, name: str, max_students: int, vk_id: int, product_id: int
    ) -> None:
        text = "Teacher {} with VK ID {} was overflow limit {} on product {}".format(
            name, vk_id, max_students, product_id
        )
        await self._send_message({"text": text})

    @asyncbackoff(attempt_timeout=1, max_tries=3, pause=0.1, deadline=5)
    async def _send_message(self, data: dict[str, Any]) -> aiohttp.ClientResponse:
        if data.get("chat_id") is None:
            data["chat_id"] = self._default_chat_id

        if data.get("parse_mode") is None:
            data["parse_mode"] = self._default_parse_mode

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with await session.post(
                url=self._send_message_url,
                data=data,
            ) as result:
                return result

    @property
    def _send_message_url(self) -> URL:
        return BASE_URL / f"bot{self._bot_token}/sendMessage"
