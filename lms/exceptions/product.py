from lms.exceptions.base import EntityNotFoundError


class ProductNotFoundError(EntityNotFoundError):
    pass


class OfferNotFoundError(EntityNotFoundError):
    def __init__(self, offer_id: int) -> None:
        self.offer_id = offer_id
