from pydantic import BaseModel, ConfigDict


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
