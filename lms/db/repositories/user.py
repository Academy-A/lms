from sqlalchemy import ScalarResult, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import User
from lms.db.repositories.base import Repository
from lms.exceptions import UserNotFoundError


class UserRepository(Repository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result: ScalarResult[User] = await self._session.scalars(stmt)
        try:
            return result.one()
        except NoResultFound as e:
            raise UserNotFoundError from e
