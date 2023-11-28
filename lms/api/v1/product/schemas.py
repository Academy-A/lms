from collections.abc import Sequence
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, PositiveInt

from lms.api.v1.schemas import PageSchema
from lms.enums import TeacherType


class DistributionFilterSchema(BaseModel):
    flow_id: int
    teacher_type: TeacherType | None


class DistributionHomeworkSchema(BaseModel):
    homework_id: PositiveInt
    filters: list[DistributionFilterSchema]


class DistributionTaskSchema(BaseModel):
    product_id: PositiveInt
    name: str
    homeworks: Sequence[DistributionHomeworkSchema]


class ReadProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    name: str
    subject_id: PositiveInt
    product_group_id: PositiveInt
    check_spreadsheet_id: str
    drive_folder_id: str
    start_date: date | None
    end_date: date | None


class ProductPageSchema(PageSchema):
    items: list[ReadProductSchema]
