from lms.exceptions.base import EntityNotFoundError


class ProductNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "Product not found"
        super().__init__(detail, *args)


class OfferNotFoundError(EntityNotFoundError):
    def __init__(self, offer_id: int) -> None:
        self.offer_id = offer_id
