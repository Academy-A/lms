from datetime import datetime
from typing import Any

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt, field_validator
from starlette_admin.fields import (
    BooleanField,
    DateTimeField,
    EnumField,
    FloatField,
    HasMany,
    HasOne,
    IntegerField,
)

from lms.admin.views.models.base import BaseModelView
from lms.generals.enums import TeacherType


class TeacherProductModel(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    teacher: Any
    product: Any
    type: TeacherType
    is_active: bool
    max_students: NonNegativeInt
    average_grade: NonNegativeFloat
    grade_counter: NonNegativeInt

    @field_validator("teacher", "product")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Field must be not none")
        return v


class TeacherProductModelView(BaseModelView):
    identity = "teacher_product"
    label = "Teacher Product"
    pydantic_model = TeacherProductModel
    fields = [
        IntegerField(name="id", label="ID", required=True, exclude_from_create=True),
        DateTimeField(
            name="created_at",
            label="Created at",
            output_format="%H:%M:%S %d.%m.%Y",
            exclude_from_create=True,
            exclude_from_list=True,
            required=True,
            form_alt_format="H:i:S d.m.Y",
        ),
        DateTimeField(
            name="updated_at",
            label="Updated at",
            output_format="%H:%M:%S %d.%m.%Y",
            exclude_from_list=True,
            exclude_from_create=True,
            required=True,
            form_alt_format="H:i:S d.m.Y",
        ),
        HasOne(name="teacher", label="Teacher", identity="teacher", required=True),
        HasOne(name="product", label="Product", identity="product", required=True),
        HasMany(name="flows", label="Flows", identity="flow"),
        EnumField(
            name="type",
            label="type",
            enum=TeacherType,
        ),
        BooleanField(
            name="is_active",
            label="Is active?",
            required=True,
        ),
        IntegerField(
            name="max_students",
            label="Max Students",
            required=True,
            exclude_from_list=True,
        ),
        FloatField(
            name="average_grade",
            label="Average Grade",
            required=True,
            exclude_from_list=True,
        ),
        IntegerField(
            name="grade_counter",
            label="Grade Counter",
            required=True,
            exclude_from_list=True,
            searchable=True,
        ),
    ]
