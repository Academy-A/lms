from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Reviewer, Teacher, TeacherProduct
from lms.db.repositories.base import Repository
from lms.exceptions import TeacherNotFoundError


class TeacherRepository(Repository[Teacher]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Teacher, session=session)

    async def find_teacher_by_teacher_product(self, teacher_product_id: int) -> Teacher:
        stmt = (
            select(Teacher)
            .join(TeacherProduct, Teacher.id == TeacherProduct.teacher_id)
            .where(TeacherProduct.id == teacher_product_id)
        )
        try:
            return (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise TeacherNotFoundError from e

    async def get_reviewers_by_product_id(self, product_id: int) -> Sequence[Reviewer]:
        query = select(Reviewer).where(Reviewer.product_id == product_id)
        return (await self._session.scalars(query)).all()
