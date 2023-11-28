from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Offer, Product
from lms.db.repositories.base import Repository
from lms.dto import PaginationData, ProductDto
from lms.exceptions import ProductNotFoundError
from lms.exceptions.base import EntityNotFoundError


class ProductRepository(Repository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Product, session=session)

    async def paginate(self, page: int, page_size: int) -> PaginationData:
        query = select(Product).order_by(Product.id)
        return await self._paginate(
            query=query,
            page=page,
            page_size=page_size,
            dto=ProductDto,
        )

    async def read_by_id(self, product_id: int) -> ProductDto:
        try:
            obj = await self._read_by_id(product_id)
            return ProductDto.from_orm(obj)
        except EntityNotFoundError as e:
            raise ProductNotFoundError from e

    async def find_product_by_offer(self, offer_id: int) -> ProductDto:
        stmt = (
            select(Product)
            .join(Offer, Product.id == Offer.id)
            .where(Offer.id == offer_id)
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
            return ProductDto.from_orm(obj)
        except NoResultFound as e:
            raise ProductNotFoundError from e
