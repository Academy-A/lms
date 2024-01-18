from pydantic import BaseModel, ConfigDict


class ParsedFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    url: str = ""
    vk_id: int | None = None
    student_id: int | None = None
    mimeType: str | None = None
    parents: str | None = None
    error: str | None = None
    essay_number: str | None = None
