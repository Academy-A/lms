from collections.abc import Iterable, Sequence
from typing import Any, NamedTuple

from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import (
    Product as ProductDb,
)
from lms.db.models import (
    Student as StudentDb,
)
from lms.db.models import (
    StudentProduct as StudentProductDb,
)
from lms.db.repositories.base import Repository
from lms.exceptions import StudentProductNotFoundError
from lms.exceptions.base import EntityNotFoundError
from lms.generals.enums import TeacherType
from lms.generals.models.student_product import StudentProduct


class StudentDistributeData(NamedTuple):
    vk_id: int
    first_name: str
    last_name: str
    teacher_product_id: int | None
    teacher_type: TeacherType | None
    is_expulsed: bool

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class StudentProductRepository(Repository[StudentProductDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=StudentProductDb, session=session)

    async def read_by_id(self, student_product_id: int) -> StudentProduct:
        try:
            obj = await self._read_by_id(object_id=student_product_id)
        except EntityNotFoundError as e:
            raise StudentProductNotFoundError from e
        return StudentProduct.model_validate(obj)

    async def find_by_student_and_product(
        self, student_id: int, product_id: int
    ) -> StudentProduct | None:
        query = select(StudentProductDb).filter_by(
            student_id=student_id,
            product_id=product_id,
        )
        student_product = (await self._session.scalars(query)).one_or_none()
        return (
            StudentProduct.model_validate(student_product) if student_product else None
        )

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
            insert(StudentProductDb)
            .values(
                student_id=student_id,
                product_id=product_id,
                offer_id=offer_id,
                cohort=cohort,
                teacher_type=teacher_type,
                teacher_product_id=teacher_product_id,
                flow_id=flow_id,
            )
            .returning(StudentProductDb)
        )
        try:
            obj = (await self._session.scalars(query)).one()
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        return StudentProduct.model_validate(obj)

    async def update(self, student_product_id: int, **kwargs: Any) -> StudentProduct:
        try:
            obj = await self._update(
                StudentProductDb.id == student_product_id,
                **kwargs,
            )
        except NoResultFound as e:
            await self._session.rollback()
            raise StudentProductNotFoundError from e
        return StudentProduct.model_validate(obj)

    async def calculate_active_students(self, teacher_product_id: int) -> int:
        stmt = select(func.count(StudentProductDb.id)).filter(
            StudentProductDb.teacher_product_id == teacher_product_id,
        )
        res = await self._session.scalar(stmt)
        return res if res is not None else 0

    async def distribute_data(
        self,
        subject_id: int,
        vk_ids: Iterable[int],
    ) -> Sequence[StudentDistributeData]:
        query = (
            select(
                StudentDb.vk_id,
                StudentDb.first_name,
                StudentDb.last_name,
                StudentProductDb.teacher_product_id,
                StudentProductDb.teacher_type,
                StudentProductDb.expulsion_at.isnot(None),
            )
            .join(StudentDb, StudentDb.id == StudentProductDb.student_id)
            .join(ProductDb, ProductDb.id == StudentProductDb.product_id)
            .where(
                ProductDb.subject_id == subject_id,
                StudentDb.vk_id.in_(vk_ids),
            )
        )
        return [
            StudentDistributeData(*res) for res in await self._session.execute(query)
        ]
