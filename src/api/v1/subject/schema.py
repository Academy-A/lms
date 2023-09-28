from pydantic import BaseModel, ConfigDict

from src.api.v1.schemas import PageSchema


class ReadSubjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    eng_name: str
    autopilot_url: str
    group_url: str


class SubjectPageSchema(PageSchema):
    items: list[ReadSubjectSchema]
