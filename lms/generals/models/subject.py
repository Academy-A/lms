from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PositiveInt
from yarl import URL


class SubjectProperties(BaseModel):
    eng_name: str
    enroll_autopilot_url: str
    group_vk_url: HttpUrl
    check_spreadsheet_id: str = ""
    check_drive_folder_id: str = ""
    check_regular_notification_folder_ids: list[str] = Field(default_factory=list)
    check_subscription_notification_folder_ids: list[str] = Field(default_factory=list)
    check_file_regex: str = ""


class Subject(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    name: str
    created_at: datetime
    updated_at: datetime
    properties: SubjectProperties

    @property
    def eng_name(self) -> str:
        return self.properties.eng_name

    @property
    def enroll_autopilot_url(self) -> str:
        return str(self.properties.enroll_autopilot_url)

    @property
    def group_vk_url(self) -> URL:
        return URL(str(self.properties.group_vk_url))

    @property
    def check_spreadsheet_id(self) -> str:
        return self.properties.check_spreadsheet_id

    @property
    def check_drive_foler_id(self) -> str:
        return self.properties.check_drive_folder_id

    @property
    def check_regular_nofitication_folder_ids(self) -> Sequence[str]:
        return self.properties.check_regular_notification_folder_ids

    @property
    def check_subscription_notification_folder_ids(self) -> Sequence[str]:
        return self.properties.check_subscription_notification_folder_ids

    @property
    def check_file_regex(self) -> str:
        return self.properties.check_file_regex


class ShortSubject(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    name: str
    created_at: datetime
    updated_at: datetime
