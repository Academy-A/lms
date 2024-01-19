from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    username: str
    password: str
    created_at: datetime
    updated_at: datetime
