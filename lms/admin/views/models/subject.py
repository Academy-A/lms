from starlette_admin.fields import IntegerField, JSONField, StringField

from lms.admin.utils import CREATED_AT_FIELD, UPDATED_AT_FIELD
from lms.admin.views.models.base import BaseModelView
from lms.generals.models.subject import Subject


class SubjectModelView(BaseModelView):
    identity = "subject"
    label = "Subject"
    pydantic_model = Subject
    fields = [
        IntegerField(name="id", label="ID", required=True),
        UPDATED_AT_FIELD,
        CREATED_AT_FIELD,
        StringField(
            name="name",
            label="Name",
            placeholder="Subject name",
            required=True,
        ),
        JSONField(
            name="properties",
            label="Properties",
            exclude_from_list=True,
        ),
    ]
