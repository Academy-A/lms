from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FileDTO:
    id: str
    name: str
    url: str | None = None
    vk_id: int | None = None
    student_id: int | None = None
    mimeType: str | None = None
    parents: str | None = None
    error: str | None = None
    essay_number: str | None = None

    def get_send_params(self) -> dict[str, Any]:
        return {
            "avtp": 1,
            "sid": self.vk_id,
            "soch": self.url,
            "title": self.essay_number,
        }
