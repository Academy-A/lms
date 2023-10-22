from enum import StrEnum, unique


@unique
class TeacherType(StrEnum):
    CURATOR = "CURATOR"
    MENTOR = "MENTOR"
