from typing import NoReturn

from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import User
from lms.db.repositories.base import Repository
from lms.dto import UserData
from lms.exceptions import LMSError, UserAlreadyExistsError, UserNotFoundError


class UserRepository(Repository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def create(self, username: str, hashed_password: str) -> UserData:
        stmt = (
            insert(User)
            .values(
                username=username,
                password=hashed_password,
            )
            .returning(User)
        )

        try:
            result: ScalarResult[User] = await self._session.scalars(stmt)
        except IntegrityError as e:
            self._raise_error(e)
        else:
            return UserData.from_orm(result.one())

    async def get_by_username(self, username: str) -> UserData:
        stmt = select(User).where(User.username == username)
        result: ScalarResult[User] = await self._session.scalars(stmt)
        try:
            return UserData.from_orm(result.one())
        except NoResultFound as e:
            raise UserNotFoundError from e

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]

        if constraint == "ix__user__username":
            raise UserAlreadyExistsError from e

        raise LMSError from e
