from datetime import datetime
from typing import Any

from sqlalchemy import ScalarResult, desc, insert, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import TeacherAssignment
from lms.adapters.db.repositories.base import Repository
from lms.exceptions import TeacherAssignmentNotFoundError


class TeacherAssignmentRepository(Repository[TeacherAssignment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=TeacherAssignment, session=session)

    async def create(
        self,
        student_product_id: int,
        teacher_product_id: int,
        assignment_at: datetime | None = None,
        removed_at: datetime | None = None,
    ) -> TeacherAssignment:
        values: dict[str, int | datetime] = {
            "teacher_product_id": teacher_product_id,
            "student_product_id": student_product_id,
        }
        if assignment_at:
            values["assignment_at"] = assignment_at
        if removed_at:
            values["removed_at"] = removed_at
        query = insert(TeacherAssignment).values(**values).returning(TeacherAssignment)
        try:
            result: ScalarResult[TeacherAssignment] = await self._session.scalars(query)
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    async def update(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> TeacherAssignment:
        try:
            return await self._update(*args, **kwargs)
        except NoResultFound as e:
            await self._session.rollback()
            raise TeacherAssignmentNotFoundError from e

    async def expulse_student(
        self, student_product_id: int, teacher_product_id: int
    ) -> None:
        now = datetime.now()
        await self.update(
            TeacherAssignment.student_product_id == student_product_id,
            TeacherAssignment.teacher_product_id == teacher_product_id,
            TeacherAssignment.removed_at.is_(None),
            removed_at=now,
        )

    async def expulse_student_safety(
        self,
        student_product_id: int,
        teacher_product_id: int,
    ) -> None:
        try:
            await self.expulse_student(
                student_product_id=student_product_id,
                teacher_product_id=teacher_product_id,
            )
        except TeacherAssignmentNotFoundError:
            pass

    async def find_last_teacher_product_id(self, student_product_id: int) -> int | None:
        query = (
            select(TeacherAssignment.teacher_product_id)
            .where(
                TeacherAssignment.student_product_id == student_product_id,
            )
            .limit(1)
            .order_by(desc(TeacherAssignment.assignment_at))
        )
        return await self._session.scalar(query)
