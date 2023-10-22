from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from lms.api.v1.schemas import PageSchema
from lms.enums import TeacherType


class DistributionSchema(BaseModel):
    homework_id: int
    teacher_types: list[TeacherType | None]


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    subject_id: int
    product_group_id: int
    check_spreadsheet_id: str
    drive_folder_id: str
    start_date: date
    end_date: date


class ProductPageSchema(PageSchema):
    items: list[ProductSchema]
