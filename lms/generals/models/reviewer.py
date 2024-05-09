from pydantic import BaseModel, ConfigDict


class CreateReviewerModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    subject_id: int
    email: str
    desired: int
    max_: int
    min_: int
    abs_max: int
    is_active: bool


class Reviewer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    first_name: str
    last_name: str
    email: str
    desired: int
    max_: int
    min_: int
    abs_max: int
    is_active: bool

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"
