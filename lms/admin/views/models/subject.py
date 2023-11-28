from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, HttpUrl, StringConstraints
from starlette_admin.fields import DateTimeField, IntegerField, StringField, URLField

from lms.admin.views.models.base import BaseModelView


class SubjectModel(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: Annotated[str, StringConstraints(max_length=64, min_length=4)]
    eng_name: Annotated[str, StringConstraints(max_length=64, min_length=4)]
    autopilot_url: HttpUrl
    group_vk_url: HttpUrl


class SubjectModelView(BaseModelView):
    identity = "subject"
    label = "Subject"
    pydantic_model = SubjectModel
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
            name="name",
            label="Name",
            placeholder="Subject name",
            required=True,
        ),
        StringField(
            name="eng_name",
            label="Eng name",
            placeholder="English subject name",
            required=True,
        ),
        URLField(
            name="autopilot_url",
            label="Autopilot URL",
            exclude_from_list=True,
            required=True,
        ),
        URLField(
            name="group_vk_url",
            label="Group VK URL",
            exclude_from_list=True,
            required=True,
        ),
    ]
