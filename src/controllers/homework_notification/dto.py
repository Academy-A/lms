from dataclasses import dataclass


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
