import logging
from http import HTTPStatus
from types import MappingProxyType
from typing import ClassVar

from aiohttp import hdrs
from pydantic import BaseModel
from yarl import URL

from lms.clients.base.client import BaseHttpClient
from lms.clients.base.handlers import parse_model
from lms.clients.base.root_handler import ResponseHandlersType
from lms.clients.base.timeout import TimeoutType
from lms.enums import TeacherType

log = logging.getLogger(__name__)

AUTOPILOT_BASE_URL = URL("https://skyauto.me/cllbck")

AUTOPILOT_TEACHER_TYPE = {
    TeacherType.CURATOR: 2,
    TeacherType.MENTOR: 3,
}


class AutopilotResponseSchema(BaseModel):
    success: bool


class Autopilot(BaseHttpClient):
    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = 2

    SEND_TEACHER_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: parse_model(AutopilotResponseSchema),
        }
    )

    SEND_HOMEWORK_HANDLERS: ResponseHandlersType = MappingProxyType(
        {
            HTTPStatus.OK: parse_model(AutopilotResponseSchema),
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
            method=hdrs.METH_GET,
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
        file_url: str,
        title: str | None,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> AutopilotResponseSchema:
        return await self._make_req(
            method=hdrs.METH_GET,
            url=self._url / target_path,
            handlers=self.SEND_HOMEWORK_HANDLERS,
            timeout=timeout,
            params={
                "avtp": 1,
                "sid": student_vk_id,
                "soch": file_url,
                "title": title,
            },
        )
