from lms.exceptions.base import EntityNotFoundError, LMSError


class UserAlreadyExistsError(LMSError):
    pass


class UserNotFoundError(EntityNotFoundError):
    pass
