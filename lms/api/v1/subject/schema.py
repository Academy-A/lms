from datetime import datetime

from pydantic import BaseModel, ConfigDict

from lms.api.v1.schemas import PageSchema


class ReadSubjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    eng_name: str
    autopilot_url: str
    group_vk_url: str


class SubjectPageSchema(PageSchema):
    items: list[ReadSubjectSchema]
