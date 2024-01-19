from collections.abc import Sequence
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class Distribution(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    subject_id: int
    data: dict[str, Any]

    def serialize_soho_homeworks(self) -> Sequence[Sequence[Any]]:
        header = [
            "soho_homework_id",
            "student_soho_id",
            "sent_to_review_at",
            "chat_url",
            "student_vk_id",
        ]
        data = []
        data.append(header)
        for hw in self.data["homeworks"]:
            data.append([v for v in hw.values()])
        return data


class DistributionFilter(BaseModel):
    flow_id: int


class DistributionHomework(BaseModel):
    homework_id: int
    filters: Sequence[DistributionFilter]


class DistributionParams(BaseModel):
    product_ids: Sequence[int]
    name: str
    homeworks: Sequence[DistributionHomework]

    @property
    def homework_ids(self) -> Sequence[int]:
        return tuple(hw.homework_id for hw in self.homeworks)
