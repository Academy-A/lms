import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateStudentSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    vk_id: int
    soho_id: int
    email: str


class EnrollStudentSchema(BaseModel):
    student: CreateStudentSchema
    offer_id: uuid.UUID


class ExpulsionStudentSchema(BaseModel):
    vk_id: int
    offer_id: uuid.UUID


class ReadStudentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    vk_id: int
    email: EmailStr


class ReadStudentProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    product_id: int
    mentor_id: int | None
    curator_id: int | None
    offer_id: int | None
    cohort: int
