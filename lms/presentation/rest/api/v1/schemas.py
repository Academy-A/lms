from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, PositiveInt


class MonitoringSchema(BaseModel):
    db_status: Literal["ok", "internal_error"]


class StatusResponseSchema(BaseModel):
    ok: bool
    status_code: PositiveInt
    message: str
