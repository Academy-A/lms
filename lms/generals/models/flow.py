from pydantic import BaseModel, ConfigDict, PositiveInt


class Flow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
