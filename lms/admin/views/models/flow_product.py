from typing import Any

from pydantic import BaseModel, PositiveInt, field_validator
from starlette_admin.fields import HasOne, IntegerField

from lms.admin.views.models.base import BaseModelView


class FlowProductModel(BaseModel):
    id: PositiveInt | None = None
    soho_id: PositiveInt
    product: Any
    flow: Any

    @field_validator("product", "flow")
    @classmethod
    def check_is_not_none(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("Field must be not none")
        return v


class FlowProductModelView(BaseModelView):
    identity = "flow_product"
    label = "Flow Product"
    pydantic_model = FlowProductModel
    fields = [
        IntegerField(name="id", label="ID", required=True, exclude_from_create=True),
        IntegerField(name="soho_id", label="Soho ID", required=True),
        HasOne(name="product", label="Product", identity="product", required=True),
        HasOne(name="flow", label="Flow", identity="flow", required=True),
    ]
