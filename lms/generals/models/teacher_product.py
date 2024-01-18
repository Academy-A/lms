from datetime import datetime

from pydantic import BaseModel, ConfigDict, NonNegativeInt, PositiveInt

from lms.generals.enums import TeacherType


class TeacherProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    teacher_id: PositiveInt
    product_id: PositiveInt
    type: TeacherType
    is_active: bool
    max_students: NonNegativeInt
    average_grade: float
    grade_counter: NonNegativeInt

    @property
    def is_mentor(self) -> bool:
        return self.type == TeacherType.MENTOR

    @property
    def is_curator(self) -> bool:
        return self.type == TeacherType.CURATOR
