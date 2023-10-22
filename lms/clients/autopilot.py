from typing import Literal

import httpx
from loguru import logger
from pydantic import BaseModel

from lms.enums import TeacherType

AUTOPILOT_TEACHER_TYPE = {
    TeacherType.CURATOR: 2,
    TeacherType.MENTOR: 3,
}


class AutopilotTeacherDataSchema(BaseModel):
    avtp: Literal[1] = 1
    sid: int
    curator: int
    option: int


async def send_teacher_to_autopilot(
    target_url: str,
    student_vk_id: int,
    teacher_vk_id: int,
    teacher_type: TeacherType,
) -> None:
    await call_autopilot(
        target_url=target_url,
        params=AutopilotTeacherDataSchema(
            sid=student_vk_id,
            curator=teacher_vk_id,
            option=AUTOPILOT_TEACHER_TYPE[teacher_type],
        ).model_dump(),
    )


async def call_autopilot(target_url: str, params: dict[str, str | int]) -> None:
    async with httpx.AsyncClient() as client:
        try:
            await client.get(target_url, params=params)
        except httpx.HTTPError as exc:
            logger.exception(
                "Got HTTP Exception for {url} - {exc}",
                url=exc.request.url,
                exc=exc,
            )
