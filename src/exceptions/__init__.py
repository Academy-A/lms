from src.exceptions.base import EntityNotFoundError, LMSError
from src.exceptions.product import ProductNotFoundError
from src.exceptions.student import (
    StudentAlreadyEnrolledError,
    StudentNotFoundError,
    StudentProductNotFoundError,
)
from src.exceptions.subject import SubjectNotFoundError
from src.exceptions.teacher import (
    TeacherAssignmentNotFoundError,
    TeacherNotFoundError,
    TeacherProductNotFoundError,
)

__all__ = [
    "EntityNotFoundError",
    "LMSError",
    "ProductNotFoundError",
    "StudentAlreadyEnrolledError",
    "StudentNotFoundError",
    "StudentProductNotFoundError",
    "SubjectNotFoundError",
    "TeacherNotFoundError",
    "TeacherProductNotFoundError",
    "TeacherAssignmentNotFoundError",
]
