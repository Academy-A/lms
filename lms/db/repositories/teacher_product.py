from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import TeacherProduct, TeacherProductFlow
from lms.db.repositories.base import Repository
from lms.enums import TeacherType
from lms.exceptions import TeacherProductNotFoundError
from lms.exceptions.base import EntityNotFoundError


class TeacherProductRepository(Repository[TeacherProduct]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=TeacherProduct, session=session)

    async def read_by_id(self, teacher_product_id: int) -> TeacherProduct:
        try:
            return await self._read_by_id(teacher_product_id)
        except EntityNotFoundError:
            raise TeacherProductNotFoundError

    async def get_for_enroll(
        self,
        product_id: int,
        teacher_type: TeacherType,
        flow_id: int | None = None,
    ) -> TeacherProduct:
        if flow_id is not None:
            teacher_product = await self._search_with_flow(
                product_id=product_id,
                teacher_type=teacher_type,
                flow_id=flow_id,
            )
            if teacher_product is not None:
                return teacher_product

        return await self._search_without_flow(
            product_id=product_id, teacher_type=teacher_type
        )

    async def _search_with_flow(
        self, product_id: int, teacher_type: TeacherType, flow_id: int
    ) -> TeacherProduct | None:
        query = (
            select(TeacherProduct)
            .join(
                TeacherProductFlow,
                TeacherProductFlow.teacher_product_id == TeacherProduct.id,
            )
            .where(
                TeacherProduct.product_id == product_id,
                TeacherProduct.type == teacher_type,
                TeacherProduct.max_students > 0,
                TeacherProduct.is_active.is_(True),
                TeacherProductFlow.flow_id == flow_id,
            )
            .order_by(desc(TeacherProduct.average_grade))
            .limit(1)
        )

        return (await self._session.scalars(query)).first()

    async def _search_without_flow(
        self,
        product_id: int,
        teacher_type: TeacherType,
    ) -> TeacherProduct:
        query = (
            select(TeacherProduct)
            .where(
                TeacherProduct.product_id == product_id,
                TeacherProduct.type == teacher_type,
                TeacherProduct.max_students > 0,
                TeacherProduct.is_active.is_(True),
            )
            .order_by(desc(TeacherProduct.average_grade))
            .limit(1)
        )

        teacher_product = (await self._session.scalars(query)).first()
        if teacher_product is None:
            raise TeacherProductNotFoundError
        return teacher_product

    async def add_grade(self, teacher_product_id: int, grade: int) -> None:
        teacher_product = await self.read_by_id(teacher_product_id=teacher_product_id)
        new_average_grade = (
            teacher_product.average_grade * teacher_product.grade_counter + grade
        ) / (teacher_product.grade_counter + 1)
        await self._update(
            TeacherProduct.id == teacher_product.id,
            average_grade=new_average_grade,
            grade_counter=teacher_product.grade_counter + 1,
        )
