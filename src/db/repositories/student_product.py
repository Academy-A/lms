from typing import Any
from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.db.models import StudentProduct
from src.db.repositories.base import Repository
from src.enums import TeacherType
from src.exceptions import StudentProductNotFoundError


class StudentProductRepository(Repository[StudentProduct]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=StudentProduct, session=session)

    async def read_by_id(self, student_product_id: int) -> StudentProduct:
        student_product = await self._read_by_id(object_id=student_product_id)
        if student_product is None:
            raise StudentProductNotFoundError
        return student_product

    async def find_by_student_and_product(
        self, student_id: int, product_id: int
    ) -> StudentProduct | None:
        query = select(StudentProduct).filter_by(
            student_id=student_id,
            product_id=product_id,
        )
        return (await self._session.scalars(query)).one_or_none()

    async def create(
        self,
        student_id: int,
        product_id: int,
        offer_id: int,
        cohort: int,
        teacher_type: TeacherType | None = None,
        teacher_product_id: int | None = None,
        flow_id: int | None = None,
    ) -> StudentProduct:
        query = (
            insert(StudentProduct)
            .values(
                student_id=student_id,
                product_id=product_id,
                offer_id=offer_id,
                cohort=cohort,
                teacher_type=teacher_type,
                teacher_product_id=teacher_product_id,
                flow_id=flow_id,
            )
            .returning(StudentProduct)
        )
        try:
            result: ScalarResult[StudentProduct] = await self._session.scalars(query)
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    async def update(self, *args: Any, **kwargs: Any) -> StudentProduct:
        try:
            return await self._update(*args, **kwargs)
        except NoResultFound as e:
            await self._session.rollback()
            raise StudentProductNotFoundError from e
