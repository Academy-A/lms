from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Offer, Product, Subject
from lms.db.repositories.base import Repository
from lms.dto import PaginationDTO
from lms.exceptions import ProductNotFoundError, SubjectNotFoundError


class ProductRepository(Repository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Product, session=session)

    async def paginate(self, page: int, page_size: int) -> PaginationDTO:
        query = select(Product).order_by(Product.name)
        return await self._paginate(
            query=query,
            page=page,
            page_size=page_size,
        )

    async def read_by_id(self, product_id: int) -> Product:
        product = await self._read_by_id(product_id)
        if product is None:
            raise ProductNotFoundError
        return product

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
