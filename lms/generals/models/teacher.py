from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class Teacher(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    vk_id: int
    first_name: str
    last_name: str

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"
