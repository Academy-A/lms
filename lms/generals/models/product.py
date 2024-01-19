from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    name: str
    subject_id: PositiveInt
    product_group_id: PositiveInt

    start_date: date | None
    end_date: date | None
