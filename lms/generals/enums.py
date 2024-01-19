from enum import StrEnum, unique


@unique
class TeacherType(StrEnum):
    CURATOR = "CURATOR"
    MENTOR = "MENTOR"


@unique
class DistributionErrorMessage(StrEnum):
    HOMEWORK_WITHOUT_VK_ID = "Не передан VK ID для поиска ученика"
    STUDENT_WITH_VK_ID_NOT_FOUND = "Ученик с данным VK ID не найден в базе"
    STUDENT_WAS_EXPULSED = "Ученик был отчислен"
    STACK_OVERFLOW = "Переполнение учеников для распределенения"
