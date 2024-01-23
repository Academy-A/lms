from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Offer as OfferDb
from lms.db.models import Product as ProductDb
from lms.db.repositories.base import PaginateMixin, Repository
from lms.exceptions import ProductNotFoundError
from lms.exceptions.base import EntityNotFoundError
from lms.generals.models.pagination import Pagination
from lms.generals.models.product import Product


class ProductRepository(PaginateMixin, Repository[ProductDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=ProductDb, session=session)

    async def paginate(self, page: int, page_size: int) -> Pagination[Product]:
        query = select(ProductDb).order_by(ProductDb.id)
        return await self._paginate(
            query=query,
            page=page,
            page_size=page_size,
            model_type=Product,
        )

    async def read_by_id(self, product_id: int) -> Product:
        try:
            obj = await self._read_by_id(product_id)
            return Product.model_validate(obj)
        except EntityNotFoundError as e:
            raise ProductNotFoundError from e

    async def find_product_by_offer(self, offer_id: int) -> Product:
        stmt = (
            select(ProductDb)
            .join(OfferDb, ProductDb.id == OfferDb.id)
            .where(OfferDb.id == offer_id)
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
            return Product.model_validate(obj)
        except NoResultFound as e:
            raise ProductNotFoundError from e

    async def read_actual_list(self, dt: datetime) -> Sequence[Product]:
        stmt = (
            select(ProductDb)
            .where(ProductDb.end_date > dt.date())
            .order_by(ProductDb.created_at)
        )
        objs = (await self._session.scalars(stmt)).all()
        return [Product.model_validate(obj) for obj in objs]
