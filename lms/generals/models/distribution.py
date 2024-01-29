from collections.abc import Sequence
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.datastructures import FormData


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
    name: str
    product_ids: Sequence[int]
    homeworks: Sequence[DistributionHomework]

    @property
    def homework_ids(self) -> Sequence[int]:
        return tuple(hw.homework_id for hw in self.homeworks)

    @classmethod
    def parse_form(cls, form: FormData) -> "DistributionParams":
        data: dict[str, Any] = {}
        for k, v in form.multi_items():
            if not isinstance(v, str):
                continue
            match k:
                case "name":
                    data[k] = v
                case "product_ids":
                    if k not in data:
                        data[k] = []
                    data[k].append(v)  # type: ignore[union-attr,arg-type]
                case "homework_ids":
                    data["homeworks"] = parse_homework_ids(v)
        return cls.model_validate(data)


def parse_homework_ids(s: str) -> list[dict[str, Any]]:
    try:
        return [
            {
                "homework_id": hw_id,
                "filters": [],
            }
            for hw_id in map(int, s.split(","))
        ]
    except ValueError:
        raise ValidationError.from_exception_data(
            title="Invalid homeworks", input_type="json", line_errors=[]
        )
