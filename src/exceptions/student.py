from src.exceptions.base import EntityNotFoundError, LMSError


class StudentAlreadyEnrolldError(LMSError):
    pass


class StudentNotFoundError(EntityNotFoundError):
    pass


class StudentProductNotFoundError(EntityNotFoundError):
    pass
