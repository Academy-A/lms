from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, PositiveInt, StringConstraints
from starlette_admin.fields import DateTimeField, IntegerField, StringField

from lms.admin.views.models.base import BaseModelView


class ProductGroupModel(BaseModel):
    id: PositiveInt | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: Annotated[str, StringConstraints(min_length=4, max_length=256)]
    eng_name: Annotated[str, StringConstraints(min_length=4, max_length=256)]


class ProductGroupModelView(BaseModelView):
    identity = "product_group"
    label = "Product Group"
    pydantic_model = ProductGroupModel
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
            exclude_from_create=True,
            exclude_from_list=True,
            required=True,
            form_alt_format="H:i:S d.m.Y",
        ),
        StringField(
            name="name",
            label="Name",
            placeholder="Name",
            minlength=4,
            maxlength=256,
            required=True,
        ),
        StringField(
            name="eng_name",
            label="Eng name",
            placeholder="English Name",
            minlength=4,
            maxlength=256,
            required=True,
        ),
    ]
