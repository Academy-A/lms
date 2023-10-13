from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import TeacherProduct, TeacherProductFlow
from src.db.repositories.base import Repository
from src.enums import TeacherType
from src.exceptions import TeacherProductNotFoundError


class TeacherProductRepository(Repository[TeacherProduct]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=TeacherProduct, session=session)

    async def find_teacher_product_for_student_on_product(
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
            .order_by(desc(TeacherProduct.rating_coef))
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
            .order_by(desc(TeacherProduct.rating_coef))
            .limit(1)
        )

        teacher_product = (await self._session.scalars(query)).first()
        if teacher_product is None:
            raise TeacherProductNotFoundError
        return teacher_product
