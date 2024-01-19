from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt

from lms.generals.enums import TeacherType


class StudentProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    student_id: PositiveInt
    product_id: PositiveInt
    teacher_product_id: PositiveInt | None
    teacher_type: TeacherType | None
    offer_id: PositiveInt
    flow_id: PositiveInt | None
    cohort: int
    teacher_grade: int | None
    teacher_graded_at: datetime | None
    expulsion_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        return self.expulsion_at is None

    @property
    def is_alone(self) -> bool:
        return self.teacher_type is None
