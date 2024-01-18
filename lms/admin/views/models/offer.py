from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    NonNegativeInt,
    PositiveInt,
    StringConstraints,
    field_validator,
)
from starlette_admin.fields import (
    DateTimeField,
    EnumField,
    HasOne,
    IntegerField,
    StringField,
)

from lms.admin.views.models.base import BaseModelView
from lms.generals.enums import TeacherType


class OfferModel(BaseModel):
    id: PositiveInt
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: Annotated[str, StringConstraints(max_length=2048)]
    cohort: NonNegativeInt
    teacher_type: None | TeacherType = None
    product: Any

    @field_validator("product")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Field must be not none")
        return v


class OfferModelView(BaseModelView):
    identity = "offer"
    label = "Offer"
    pydantic_model = OfferModel
    fields = [
        IntegerField(name="id", label="ID", required=True),
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
        StringField(
            name="name",
            label="Name",
            maxlength=2048,
            required=True,
        ),
        HasOne(
            name="product",
            label="Product",
            identity="product",
            required=True,
        ),
        IntegerField(name="cohort", label="Cohort", required=True),
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
    ]
