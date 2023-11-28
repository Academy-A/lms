from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, PositiveInt, StringConstraints, field_validator
from starlette_admin.fields import (
    DateField,
    DateTimeField,
    HasOne,
    IntegerField,
    StringField,
)

from lms.admin.views.models.base import BaseModelView


class ProductModel(BaseModel):
    id: PositiveInt | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: Annotated[str, StringConstraints(max_length=1024, min_length=8, strict=True)]
    subject: Any
    product_group: Any
    check_spreadsheet_id: Annotated[str, StringConstraints(max_length=256, strict=True)]
    drive_folder_id: Annotated[str, StringConstraints(max_length=256, strict=True)]

    @field_validator("subject", "product_group")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Field must be not none")
        return v


class ProductModelView(BaseModelView):
    identity = "product"
    label = "Product"
    pydantic_model = ProductModel
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
            placeholder="Product name",
            minlength=4,
            maxlength=1024,
            required=True,
        ),
        HasOne(
            name="subject",
            label="Subject",
            identity="subject",
            required=True,
        ),
        HasOne(
            name="product_group",
            label="Product Group",
            identity="product_group",
            required=True,
        ),
        StringField(
            name="check_spreadsheet_id",
            label="Check Spreadsheet ID",
            maxlength=256,
            required=True,
            exclude_from_list=True,
        ),
        StringField(
            name="drive_folder_id",
            label="Drive Folder ID",
            maxlength=256,
            required=True,
            exclude_from_list=True,
        ),
        DateField(
            name="start_date",
            label="Start Date",
            output_format="%d.%m.%Y",
            search_format="DD.MM.YYYY",
            exclude_from_list=True,
            form_alt_format="d.m.Y",
        ),
        DateField(
            name="end_date",
            label="End Date",
            output_format="%d.%m.%Y",
            search_format="DD.MM.YYYY",
            exclude_from_list=True,
            form_alt_format="d.m.Y",
        ),
    ]
