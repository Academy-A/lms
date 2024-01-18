from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class Subject(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    name: str
    eng_name: str
    autopilot_url: str
    group_vk_url: str
    check_spreadsheet_id: str
    drive_folder_id: str
    created_at: datetime
    updated_at: datetime
