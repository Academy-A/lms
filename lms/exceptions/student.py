from lms.exceptions.base import EntityNotFoundError, LMSError


class StudentAlreadyEnrolledError(LMSError):
    pass


class StudentNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "Student not found"
        super().__init__(detail, *args)


class StudentProductNotFoundError(EntityNotFoundError):
    def __init__(self, detail: str = "Entity not found", *args: object) -> None:
        detail = "StudentProduct not found"
        super().__init__(detail, *args)


class StudentVKIDAlreadyUsedError(LMSError):
    pass


class StudentProductHasNotTeacherError(LMSError):
    pass


class StudentProductAlreadyExpulsedError(LMSError):
    pass
