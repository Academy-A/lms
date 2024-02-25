from sqlalchemy import desc, select, text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import (
    TeacherProduct as TeacherProductDb,
)
from lms.db.models import (
    TeacherProductFlow as TeacherProductFlowDb,
)
from lms.db.repositories.base import Repository
from lms.exceptions import TeacherProductNotFoundError
from lms.exceptions.base import EntityNotFoundError
from lms.generals.enums import TeacherType
from lms.generals.models.teacher_dashboard import TeacherDashboardRow
from lms.generals.models.teacher_product import TeacherProduct


class TeacherProductRepository(Repository[TeacherProductDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=TeacherProductDb, session=session)

    async def read_by_id(self, teacher_product_id: int) -> TeacherProduct:
        try:
            obj = await self._read_by_id(teacher_product_id)
        except EntityNotFoundError as e:
            raise TeacherProductNotFoundError from e
        return TeacherProduct.model_validate(obj)

    async def find_by_teacher_and_product(
        self, teacher_id: int, product_id: int
    ) -> TeacherProduct:
        stmt = select(TeacherProductDb).filter_by(
            teacher_id=teacher_id, product_id=product_id
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise TeacherProductNotFoundError from e
        return TeacherProduct.model_validate(obj)

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
            select(TeacherProductDb)
            .join(
                TeacherProductFlowDb,
                TeacherProductFlowDb.teacher_product_id == TeacherProductDb.id,
            )
            .where(
                TeacherProductDb.product_id == product_id,
                TeacherProductDb.type == teacher_type,
                TeacherProductDb.max_students > 0,
                TeacherProductDb.is_active.is_(True),
                TeacherProductFlowDb.flow_id == flow_id,
            )
            .order_by(desc(TeacherProductDb.rating_coef))
            .limit(1)
        )

        obj = (await self._session.scalars(query)).first()
        return TeacherProduct.model_validate(obj) if obj else None

    async def _search_without_flow(
        self,
        product_id: int,
        teacher_type: TeacherType,
    ) -> TeacherProduct:
        query = (
            select(TeacherProductDb)
            .where(
                TeacherProductDb.product_id == product_id,
                TeacherProductDb.type == teacher_type,
                TeacherProductDb.max_students > 0,
                TeacherProductDb.is_active.is_(True),
            )
            .order_by(desc(TeacherProductDb.rating_coef))
            .limit(1)
        )

        obj = (await self._session.scalars(query)).first()
        if obj is None:
            raise TeacherProductNotFoundError
        return TeacherProduct.model_validate(obj)

    async def add_grade(self, teacher_product_id: int, grade: int) -> None:
        teacher_product = await self.read_by_id(teacher_product_id=teacher_product_id)
        new_average_grade = (
            teacher_product.average_grade * teacher_product.grade_counter + grade
        ) / (teacher_product.grade_counter + 1)
        await self._update(
            TeacherProductDb.id == teacher_product.id,
            average_grade=new_average_grade,
            grade_counter=teacher_product.grade_counter + 1,
        )

    async def get_dashboard_data(self, product_id: int) -> list[TeacherDashboardRow]:
        stmt = """
            SELECT
                teacher_product.id,
                CONCAT(teacher.first_name, ' ', teacher.last_name) AS name,
                teacher.vk_id,
                teacher_product.is_active,
                teacher_product.type,
                teacher_product.max_students,
                CASE
                    WHEN tmp.filled IS NOT NULL THEN tmp.filled
                    ELSE 0
                END AS filled,
                teacher_product.average_grade,
                teacher_product.grade_counter,
                CASE
                    WHEN tpf.flows IS NOT NULL THEN tpf.flows
                    ELSE ''
                END AS flows
            FROM teacher_product
            JOIN teacher ON teacher_product.teacher_id = teacher.id
            LEFT JOIN (
                SELECT
                    teacher_product_id,
                    COUNT(*) AS filled
                FROM student_product GROUP BY teacher_product_id
            ) tmp ON teacher_product.id = tmp.teacher_product_id
            LEFT JOIN (
                SELECT
                    teacher_product_id,
                    STRING_AGG(CAST(flow_id AS VARCHAR(5)), ', ') AS flows
                FROM teacher_product_flow
                group by teacher_product_id
            ) tpf ON teacher_product.id = tpf.teacher_product_id
            WHERE teacher_product.product_id = :product_id
            ORDER BY teacher.first_name
        """
        result = await self._session.execute(text(stmt), {"product_id": product_id})
        return [TeacherDashboardRow(*r) for r in result]
