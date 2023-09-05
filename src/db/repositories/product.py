from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Offer, Product, Subject
from src.db.repositories.base import Repository
from src.exceptions import ProductNotFoundError, SubjectNotFoundError


class ProductRepository(Repository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Product, session=session)

    async def find_product_by_offer(self, offer_id: int) -> Product:
        stmt = (
            select(Product)
            .join(Offer, Product.id == Offer.id)
            .where(Offer.id == offer_id)
        )
        try:
            return (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise ProductNotFoundError from e

    async def find_subject_by_product(self, product_id: int) -> Subject:
        stmt = (
            select(Subject)
            .join(Product, Subject.id == Product.subject_id)
            .where(Product.id == product_id)
        )
        try:
            return (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise SubjectNotFoundError from e
