from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Reviewer as ReviewerDb
from lms.db.repositories.base import Repository
from lms.generals.models.reviewer import Reviewer


class ReviewerRepository(Repository[ReviewerDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=ReviewerDb, session=session)

    async def get_by_subject_id(
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
        objs = (await self._session.scalars(query)).all()
        return [Reviewer.model_validate(obj) for obj in objs]
