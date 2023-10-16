from src.exceptions.base import EntityNotFoundError, LMSError
from src.exceptions.product import OfferNotFoundError, ProductNotFoundError
from src.exceptions.soho import SohoNotFoundError
from src.exceptions.student import (
    StudentAlreadyEnrolledError,
    StudentNotFoundError,
    StudentProductNotFoundError,
    StudentVKIDAlreadyUsedError,
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
    "OfferNotFoundError",
    "ProductNotFoundError",
    "SohoNotFoundError",
    "StudentAlreadyEnrolledError",
    "StudentNotFoundError",
    "StudentProductNotFoundError",
    "StudentVKIDAlreadyUsedError",
    "SubjectNotFoundError",
    "TeacherAssignmentNotFoundError",
    "TeacherNotFoundError",
    "TeacherProductNotFoundError",
]
