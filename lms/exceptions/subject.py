from lms.exceptions.base import EntityNotFoundError


class SubjectNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "Subject not found"
        super().__init__(detail, *args)
