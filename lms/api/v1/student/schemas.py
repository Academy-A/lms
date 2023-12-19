from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainValidator,
    PositiveInt,
    WithJsonSchema,
)
from pydantic.dataclasses import dataclass


@dataclass
class OfferFlow:
    offer_id: PositiveInt
    flow_id: PositiveInt


def parse_offer_flow(v: Any) -> OfferFlow:
    if isinstance(v, OfferFlow):
        return v
    str_offer_ids, str_flow_ids = v.split(":")
    flow_id = next(map(int, str_flow_ids.split(",")))
    offer_id = next(map(int, str_offer_ids.split(",")))
    return OfferFlow(offer_id=offer_id, flow_id=flow_id)


OfferFlowType = Annotated[
    OfferFlow | str,
    PlainValidator(lambda v: parse_offer_flow(v)),
    WithJsonSchema({"type": "string"}, mode="serialization"),
    WithJsonSchema({"type": "string"}, mode="validation"),
]


class CreateStudentSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    raw_soho_flow_id: OfferFlowType
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
