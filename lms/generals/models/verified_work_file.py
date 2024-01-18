from pydantic import BaseModel, ConfigDict


class VerifiedWorkFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    student_id: int | None
    file_id: str
    name: str
    url: str
