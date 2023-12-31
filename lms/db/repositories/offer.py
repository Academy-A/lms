from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Offer
from lms.db.repositories.base import Repository
from lms.exceptions.base import EntityNotFoundError
from lms.exceptions.product import OfferNotFoundError


class OfferRepository(Repository[Offer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Offer, session=session)

    async def read_by_id(self, offer_id: int) -> Offer:
        try:
            return await self._read_by_id(object_id=offer_id)
        except EntityNotFoundError as e:
            raise OfferNotFoundError(offer_id=offer_id) from e
