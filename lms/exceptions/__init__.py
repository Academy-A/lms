from lms.exceptions.base import EntityNotFoundError, LMSError
from lms.exceptions.distribution import DistributionNotFoundError
from lms.exceptions.product import OfferNotFoundError, ProductNotFoundError
from lms.exceptions.soho import SohoNotFoundError
from lms.exceptions.student import (
    StudentAlreadyEnrolledError,
    StudentNotFoundError,
    StudentProductAlreadyExpulsedError,
    StudentProductHasNotTeacherError,
    StudentProductNotFoundError,
    StudentVKIDAlreadyUsedError,
)
from lms.exceptions.subject import SubjectNotFoundError
from lms.exceptions.teacher import (
    TeacherAssignmentNotFoundError,
    TeacherNotFoundError,
    TeacherProductNotFoundError,
)
from lms.exceptions.user import UserAlreadyExistsError, UserNotFoundError

__all__ = [
    "DistributionNotFoundError",
    "EntityNotFoundError",
    "LMSError",
    "OfferNotFoundError",
    "ProductNotFoundError",
    "SohoNotFoundError",
    "StudentAlreadyEnrolledError",
    "StudentNotFoundError",
    "StudentProductAlreadyExpulsedError",
    "StudentProductHasNotTeacherError",
    "StudentProductNotFoundError",
    "StudentVKIDAlreadyUsedError",
    "SubjectNotFoundError",
    "TeacherAssignmentNotFoundError",
    "TeacherNotFoundError",
    "TeacherProductNotFoundError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
]
