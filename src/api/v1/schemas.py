from typing import Literal

from pydantic import BaseModel


class MonitoringSchema(BaseModel):
    status: Literal["ok"]


class StatusResponseSchema(BaseModel):
    ok: bool
    status_code: int
    message: str
