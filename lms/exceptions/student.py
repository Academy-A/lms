from lms.exceptions.base import EntityNotFoundError, LMSError


class StudentAlreadyEnrolledError(LMSError):
    pass


class StudentNotFoundError(EntityNotFoundError):
    pass


class StudentProductNotFoundError(EntityNotFoundError):
    pass


class StudentVKIDAlreadyUsedError(LMSError):
    pass


class StudentProductHasNotTeacherError(LMSError):
    pass
