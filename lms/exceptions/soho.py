from lms.exceptions.base import EntityNotFoundError


class SohoNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "Soho not found"
        super().__init__(detail, *args)
