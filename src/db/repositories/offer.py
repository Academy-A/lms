from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Offer
from src.db.repositories.base import Repository
from src.exceptions.product import OfferNotFoundError


class OfferRepository(Repository[Offer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Offer, session=session)

    async def read_by_id(self, offer_id: int) -> Offer:
        offer = await self._read_by_id(object_id=offer_id)
        if offer is None:
            raise OfferNotFoundError(offer_id=offer_id)
        return offer
