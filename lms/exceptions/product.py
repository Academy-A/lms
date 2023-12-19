from lms.exceptions.base import EntityNotFoundError


class ProductNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "Product not found"
        super().__init__(detail, *args)


class OfferNotFoundError(EntityNotFoundError):
    def __init__(
        self, offer_id: int, detail: str = "Entity not found", *args: object
    ) -> None:
        self.offer_id = offer_id
        super().__init__(detail, *args)
