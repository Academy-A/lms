from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class SohoAccount(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    student_id: PositiveInt
    email: str
    created_at: datetime
    updated_at: datetime
