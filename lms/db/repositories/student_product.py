from typing import Any

from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import StudentProduct
from lms.db.repositories.base import Repository
from lms.dto import StudentProductData
from lms.enums import TeacherType
from lms.exceptions import StudentProductNotFoundError
from lms.exceptions.base import EntityNotFoundError


class StudentProductRepository(Repository[StudentProduct]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=StudentProduct, session=session)

    async def read_by_id(self, student_product_id: int) -> StudentProductData:
        try:
            obj = await self._read_by_id(object_id=student_product_id)
        except EntityNotFoundError as e:
            raise StudentProductNotFoundError from e
        return StudentProductData.from_orm(obj)

    async def find_by_student_and_product(
        self, student_id: int, product_id: int
    ) -> StudentProductData | None:
        query = select(StudentProduct).filter_by(
            student_id=student_id,
            product_id=product_id,
        )
        student_product = (await self._session.scalars(query)).one_or_none()
        return StudentProductData.from_orm(student_product) if student_product else None

    async def create(
        self,
        student_id: int,
        product_id: int,
        offer_id: int,
        cohort: int,
        teacher_type: TeacherType | None = None,
        teacher_product_id: int | None = None,
        flow_id: int | None = None,
    ) -> StudentProductData:
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
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return StudentProductData.from_orm(result.one())

    async def update(self, *args: Any, **kwargs: Any) -> StudentProductData:
        try:
            obj = await self._update(*args, **kwargs)
            return StudentProductData.from_orm(obj)
        except NoResultFound as e:
            await self._session.rollback()
            raise StudentProductNotFoundError from e
