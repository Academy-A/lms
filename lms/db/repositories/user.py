from typing import NoReturn

from sqlalchemy import ScalarResult, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import User as UserDb
from lms.db.repositories.base import Repository
from lms.exceptions import LMSError, UserAlreadyExistsError, UserNotFoundError
from lms.generals.models.user import User


class UserRepository(Repository[UserDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=UserDb, session=session)

    async def create(self, username: str, hashed_password: str) -> User:
        stmt = (
            insert(UserDb)
            .values(
                username=username,
                password=hashed_password,
            )
            .returning(UserDb)
        )

        try:
            result: ScalarResult[UserDb] = await self._session.scalars(stmt)
        except IntegrityError as e:
            self._raise_error(e)
        return User.model_validate(result.one())

    async def get_by_username(self, username: str) -> User:
        stmt = select(UserDb).where(UserDb.username == username)

        try:
            obj = (await self._session.scalars(stmt)).one()
        except NoResultFound as e:
            raise UserNotFoundError from e
        return User.model_validate(obj)

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]

        if constraint == "ix__user__username":
            raise UserAlreadyExistsError from e

        raise LMSError from e
