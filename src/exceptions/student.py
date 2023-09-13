from src.exceptions.base import EntityNotFoundError, LMSError


class StudentAlreadyEnrolledError(LMSError):
    pass


class StudentNotFoundError(EntityNotFoundError):
    pass


class StudentProductNotFoundError(EntityNotFoundError):
    pass
