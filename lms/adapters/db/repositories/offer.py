from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Offer as OfferDb
from lms.adapters.db.repositories.base import Repository
from lms.exceptions.base import EntityNotFoundError
from lms.exceptions.product import OfferNotFoundError
from lms.generals.models.offer import Offer


class OfferRepository(Repository[OfferDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=OfferDb, session=session)

    async def read_by_id(self, offer_id: int) -> Offer:
        try:
            obj = await self._read_by_id(object_id=offer_id)
        except EntityNotFoundError as e:
            raise OfferNotFoundError(offer_id=offer_id) from e
        return Offer.model_validate(obj)
