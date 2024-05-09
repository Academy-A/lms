from collections.abc import Sequence

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Reviewer as ReviewerDb
from lms.db.repositories.base import Repository
from lms.generals.models.reviewer import CreateReviewerModel, Reviewer


class ReviewerRepository(Repository[ReviewerDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=ReviewerDb, session=session)

    async def create(self, new_reviewer: CreateReviewerModel) -> Reviewer:
        query = (
            insert(ReviewerDb)
            .values(
                subject_id=new_reviewer.subject_id,
                first_name=new_reviewer.first_name,
                laste_name=new_reviewer.last_name,
                email=new_reviewer.email,
                desired=new_reviewer.desired,
                max_=new_reviewer.max_,
                min_=new_reviewer.min_,
                abs_max=new_reviewer.abs_max,
                is_active=new_reviewer.is_active,
            )
            .returning(ReviewerDb)
        )
        result = await self._session.scalars(query)
        return Reviewer.model_validate(result.one())

    async def get_list_by_subject_id(
        self, subject_id: int, is_acitve: bool = True
    ) -> Sequence[Reviewer]:
        query = (
            select(ReviewerDb)
            .where(
                ReviewerDb.subject_id == subject_id,
                ReviewerDb.is_active.is_(is_acitve),
            )
            .order_by(ReviewerDb.id)
        )
        result = await self._session.scalars(query)
        return [Reviewer.model_validate(obj) for obj in result]
