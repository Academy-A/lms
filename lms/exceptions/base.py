class LMSError(Exception):
    pass


class EntityNotFoundError(LMSError):
    def __init__(self, detail: str = "Entity not found", *args: object) -> None:
        self.detail = detail
        super().__init__(*args)
