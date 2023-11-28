from dataclasses import dataclass


@dataclass(frozen=True)
class FileData:
    id: str
    name: str
    url: str = ""
    vk_id: int | None = None
    student_id: int | None = None
    mimeType: str | None = None
    parents: str | None = None
    error: str | None = None
    essay_number: str | None = None
