from typing import Annotated, Any

from pydantic import (
    BaseModel,
    EmailStr,
    NonNegativeInt,
    StringConstraints,
    field_validator,
)
from starlette_admin.fields import (
    BooleanField,
    DateTimeField,
    EmailField,
    HasOne,
    IntegerField,
    StringField,
)

from lms.admin.views.models.base import BaseModelView


class ReviewerModel(BaseModel):
    id: int | None = None
    first_name: Annotated[str, StringConstraints(max_length=128, strict=True)]
    last_name: Annotated[str, StringConstraints(max_length=128, strict=True)]
    email: EmailStr
    desired: NonNegativeInt
    max_: NonNegativeInt
    abs_max: NonNegativeInt
    is_active: bool
    product: Any
    teacher_product: Any | None = None

    @field_validator("product")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Product must be not none")
        return v


class ReviewerModelView(BaseModelView):
    identity = "reviewer"
    label = "Reviewer"
    pydantic_model = ReviewerModel
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
        StringField(
            name="first_name",
            label="First name",
            required=True,
        ),
        StringField(
            name="last_name",
            label="Last name",
            required=True,
        ),
        HasOne(
            name="product",
            label="Product",
            identity="product",
            required=True,
        ),
        HasOne(
            name="teacher_product",
            label="Teacher product",
            identity="teacher_product",
            required=False,
        ),
        EmailField(
            name="email",
            label="Email",
            required=True,
            exclude_from_list=True,
        ),
        IntegerField(
            name="desired",
            label="Desired",
            required=True,
        ),
        IntegerField(
            name="max_",
            label="Max",
            required=True,
        ),
        IntegerField(
            name="abs_max",
            label="Abs max",
            required=True,
        ),
        BooleanField(
            name="is_active",
            label="Is active?",
            required=True,
        ),
    ]
