from datetime import datetime
from typing import Any

from pydantic import BaseModel, PositiveInt, field_validator, model_validator
from starlette_admin.fields import DateTimeField, EnumField, HasOne, IntegerField

from lms.admin.views.models.base import BaseModelView
from lms.enums import TeacherType


class StudentProductModel(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    student: Any
    product: Any
    teacher_product: Any | None
    teacher_type: TeacherType | None
    offer: Any
    flow: Any | None
    cohort: PositiveInt
    teacher_grade: PositiveInt | None
    teacher_graded_at: datetime | None
    expulsion_at: datetime | None

    @field_validator("student", "product", "offer")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Field must be not none")
        return v

    @model_validator(mode="after")
    def check_teacher_type(self) -> "StudentProductModel":
        if (self.teacher_type is None) is (self.teacher_product is None):
            return self
        raise ValueError("Teacher Type does not match wih teacher product")


class StudentProductModelView(BaseModelView):
    identity = "student_product"
    label = "Student Product"
    pydantic_model = StudentProductModel
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
        HasOne(
            name="student",
            label="Student",
            identity="student",
            required=True,
            searchable=True,
        ),
        HasOne(name="product", label="Product", identity="product", required=True),
        HasOne(
            name="teacher_product", label="Teacher Product", identity="teacher_product"
        ),
        EnumField(
            name="teacher_type",
            label="Teacher Type",
            choices=tuple(
                (v, t)
                for v, t in zip(
                    (None, TeacherType.CURATOR, TeacherType.MENTOR),
                    ("Empty", "Curator", "Mentor"),
                )
            ),
            required=True,
            coerce=lambda x: x if x != "None" else None,
        ),
        HasOne(
            name="offer",
            label="Offer",
            identity="offer",
            required=True,
            exclude_from_list=True,
        ),
        HasOne(name="flow", label="Flow", identity="flow", exclude_from_list=True),
        IntegerField(
            name="cohort", label="Cohort", required=True, exclude_from_list=True
        ),
        IntegerField(
            name="teacher_grade",
            label="Teacher Grade",
            required=False,
            exclude_from_list=True,
        ),
        DateTimeField(
            name="teacher_graded_at",
            label="Teacher Graded at",
            required=False,
            exclude_from_list=True,
        ),
        DateTimeField(
            name="expulsion_at",
            label="Expulsion at",
            required=False,
            exclude_from_list=True,
        ),
    ]
