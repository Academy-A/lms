import logging
from collections.abc import Awaitable, Callable
from http import HTTPStatus
from inspect import iscoroutinefunction
from types import MappingProxyType
from typing import ClassVar, TypeVar

from aiohttp import ClientResponse
from asyncly import BaseHttpClient, ResponseHandlersType, TimeoutType
from pydantic import BaseModel
from yarl import URL

from lms.generals.enums import TeacherType

log = logging.getLogger(__name__)

AUTOPILOT_BASE_URL = URL("https://skyauto.me/cllbck")

AUTOPILOT_TEACHER_TYPE = {
    TeacherType.CURATOR: 2,
    TeacherType.MENTOR: 3,
}

RT = TypeVar("RT")


def text_parser(
    parser: Callable[[str], RT],
) -> Callable[[ClientResponse], Awaitable[RT]]:
    async def _parse(response: ClientResponse) -> RT:
        resp_data = await response.text()
        if iscoroutinefunction(parser):
            return await parser(resp_data)
        else:
            return parser(resp_data)

    return _parse


class AutopilotResponseSchema(BaseModel):
    success: bool


class Autopilot(BaseHttpClient):
    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = 2

    SEND_TEACHER_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: text_parser(parser=lambda x: x),
        }
    )

    SEND_HOMEWORK_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: text_parser(parser=lambda x: x),
        }
    )

    async def send_teacher(
        self,
        target_path: str,
        student_vk_id: int,
        teacher_vk_id: int,
        teacher_type: TeacherType,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> AutopilotResponseSchema:
        return await self._make_req(
            method="GET",
            url=self._url / target_path,
            handlers=self.SEND_TEACHER_HANDLERS,
            timeout=timeout,
            params={
                "avtp": 1,
                "sid": student_vk_id,
                "curator": teacher_vk_id,
                "option": AUTOPILOT_TEACHER_TYPE[teacher_type],
            },
        )

    async def send_homework(
        self,
        target_path: str,
        student_vk_id: int | None,
        subject_eng: str,
        file_url: str,
        title: str | None,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> AutopilotResponseSchema:
        return await self._make_req(
            method="GET",
            url=self._url / target_path,
            handlers=self.SEND_HOMEWORK_HANDLERS,
            timeout=timeout,
            params={
                "avtp": 1,
                "sid": student_vk_id,
                "soch": file_url,
                "title": title,
                "subject": subject_eng,
            },
        )
