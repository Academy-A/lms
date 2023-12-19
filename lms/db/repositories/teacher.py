from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Teacher, TeacherProduct
from lms.db.repositories.base import Repository
from lms.dto import TeacherDto
from lms.exceptions import TeacherNotFoundError


class TeacherRepository(Repository[Teacher]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Teacher, session=session)

    async def read_by_vk_id(self, vk_id: int) -> TeacherDto:
        stmt = select(Teacher).filter_by(vk_id=vk_id)
        try:
            obj = (await self._session.scalars(stmt)).one()
            return TeacherDto.from_orm(obj)
        except NoResultFound as e:
            raise TeacherNotFoundError from e

    async def find_teacher_by_teacher_product(
        self,
        teacher_product_id: int,
    ) -> TeacherDto:
        stmt = (
            select(Teacher)
            .join(TeacherProduct, Teacher.id == TeacherProduct.teacher_id)
            .where(TeacherProduct.id == teacher_product_id)
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise TeacherNotFoundError from e
        return TeacherDto.from_orm(obj)
