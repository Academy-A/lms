from dataclasses import dataclass


@dataclass
class NewStudentData:
    vk_id: int
    soho_id: int
    email: str
    first_name: str | None
    last_name: str | None
