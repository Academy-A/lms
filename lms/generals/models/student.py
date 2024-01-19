from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt
from pydantic.dataclasses import dataclass


class Student(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    vk_id: int
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime


@dataclass
class NewStudent:
    vk_id: int
    soho_id: int
    email: str
    first_name: str | None
    last_name: str | None
    flow_id: int
