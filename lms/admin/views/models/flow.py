from datetime import datetime

from pydantic import BaseModel, PositiveInt
from starlette_admin.fields import DateTimeField, IntegerField

from lms.admin.views.models.base import BaseModelView


class FlowModel(BaseModel):
    id: PositiveInt
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FlowModelView(BaseModelView):
    identity = "flow"
    label = "Flow"
    pydantic_model = FlowModel
    fields = [
        IntegerField(name="id", label="ID", required=True),
        DateTimeField(
            name="created_at",
            label="Created at",
            output_format="%H:%M:%S %d.%m.%Y",
            exclude_from_create=True,
            exclude_from_list=False,
            required=True,
            form_alt_format="H:i:S d.m.Y",
            read_only=True,
        ),
        DateTimeField(
            name="updated_at",
            label="Updated at",
            output_format="%H:%M:%S %d.%m.%Y",
            exclude_from_create=True,
            exclude_from_list=False,
            required=True,
            form_alt_format="H:i:S d.m.Y",
            read_only=True,
        ),
    ]
