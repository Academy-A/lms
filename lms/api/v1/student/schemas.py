from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class CreateStudentSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    raw_soho_flow_id: str
    vk_id: PositiveInt
    soho_id: PositiveInt
    email: str


class EnrollStudentSchema(BaseModel):
    student: CreateStudentSchema
    offer_ids: list[PositiveInt]


class ExpulsionStudentSchema(BaseModel):
    vk_id: PositiveInt
    product_id: PositiveInt


class ReadStudentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    first_name: str
    last_name: str
    vk_id: PositiveInt


class ReadStudentProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: PositiveInt
    product_id: PositiveInt
    teacher_product_id: PositiveInt | None
    offer_id: PositiveInt | None
    cohort: int


class ChangeVKIDSchema(BaseModel):
    vk_id: PositiveInt


class GradeTeacherSchema(BaseModel):
    grade: int = Field(ge=0, le=5)
    product_id: PositiveInt


class ChangeTeacherSchema(BaseModel):
    product_id: PositiveInt
    student_vk_id: PositiveInt
    teacher_vk_id: PositiveInt
