from lms.exceptions.base import EntityNotFoundError


class SohoNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "SohoAccount not found"
        super().__init__(detail, *args)
