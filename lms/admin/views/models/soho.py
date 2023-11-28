from typing import Any

from pydantic import BaseModel, EmailStr, field_validator
from starlette_admin.fields import DateTimeField, EmailField, HasOne, IntegerField

from lms.admin.views.models.base import BaseModelView


class SohoModel(BaseModel):
    id: int
    email: EmailStr
    student: Any

    @field_validator("student")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Student must be not none")
        return v


class SohoModelView(BaseModelView):
    identity = "soho"
    label = "Soho"
    pydantic_model = SohoModel
    fields = [
        IntegerField(name="id", label="ID", required=True),
        DateTimeField(
            name="created_at",
            label="Created at",
            output_format="%H:%M:%S %d.%m.%Y",
            exclude_from_list=True,
            exclude_from_create=True,
            required=True,
        ),
        DateTimeField(
            name="updated_at",
            label="Updated at",
            output_format="%H:%M:%S %d.%m.%Y",
            exclude_from_list=True,
            exclude_from_create=True,
            required=True,
        ),
        EmailField(name="email", label="Email", maxlength=128, required=True),
        HasOne(name="student", label="Student", identity="student", required=True),
    ]
