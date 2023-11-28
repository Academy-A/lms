from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, PositiveInt, StringConstraints
from starlette_admin.fields import (
    DateTimeField,
    IntegerField,
    StringField,
    TextAreaField,
)

from lms.admin.views.models.base import BaseModelView


class SettingModel(BaseModel):
    id: PositiveInt | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    key: Annotated[str, StringConstraints(max_length=128)]
    description: Annotated[str, StringConstraints(max_length=512)]
    value: Annotated[str, StringConstraints(max_length=4096)]


class SettingModelView(BaseModelView):
    identity = "setting"
    label = "Setting"
    pydantic_model = SettingModel
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
        StringField(name="key", label="Key", required=True, maxlength=128),
        StringField(
            name="description", label="Description", required=True, maxlength=512
        ),
        TextAreaField(
            name="value",
            label="Value",
            required=True,
            maxlength=4096,
            exclude_from_list=True,
        ),
    ]
