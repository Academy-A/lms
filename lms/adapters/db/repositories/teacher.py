from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Teacher as TeacherDb
from lms.adapters.db.models import TeacherProduct as TeacherProductDb
from lms.adapters.db.repositories.base import Repository
from lms.exceptions import TeacherNotFoundError
from lms.generals.models.teacher import Teacher


class TeacherRepository(Repository[TeacherDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=TeacherDb, session=session)

    async def read_by_vk_id(self, vk_id: int) -> Teacher:
        stmt = select(TeacherDb).filter_by(vk_id=vk_id)
        try:
            obj = (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise TeacherNotFoundError from e
        return Teacher.model_validate(obj)

    async def find_teacher_by_teacher_product(
        self,
        teacher_product_id: int,
    ) -> Teacher:
        stmt = (
            select(TeacherDb)
            .join(TeacherProductDb, TeacherDb.id == TeacherProductDb.teacher_id)
            .where(TeacherProductDb.id == teacher_product_id)
        )
        try:
            obj = (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise TeacherNotFoundError from e
        return Teacher.model_validate(obj)
