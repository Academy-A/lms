from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt

from lms.generals.enums import TeacherType


class Offer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    product_id: PositiveInt
    name: str
    cohort: int
    teacher_type: TeacherType | None
    created_at: datetime
    updated_at: datetime

    @property
    def is_alone(self) -> bool:
        return self.teacher_type is None
