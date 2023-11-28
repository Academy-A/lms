from pydantic import BaseModel
from starlette_admin.fields import DateTimeField, IntegerField, StringField

from lms.admin.views.models.base import BaseModelView


class StudentModel(BaseModel):
    first_name: str
    last_name: str
    vk_id: int


class StudentModelView(BaseModelView):
    identity = "student"
    label = "Student"
    icon = "fa fa-blog"
    pydantic_model = StudentModel
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
            placeholder="First name",
            maxlength=128,
            required=True,
        ),
        StringField(
            name="last_name",
            label="Last name",
            placeholder="Last name",
            maxlength=128,
            required=True,
        ),
        IntegerField(
            name="vk_id",
            label="VK ID",
            required=True,
        ),
    ]
