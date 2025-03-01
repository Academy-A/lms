from typing import NoReturn

from sqlalchemy import ScalarResult, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import User as UserDb
from lms.adapters.db.repositories.base import Repository
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

    async def update_password_by_username(
        self, username: str, hashed_password: str
    ) -> User:
        stmt = (
            update(UserDb)
            .values(password=hashed_password)
            .where(UserDb.username == username)
            .returning(UserDb)
        )
        try:
            result = await self._session.scalars(stmt)
            return User.model_validate(result.one())
        except IntegrityError as e:
            self._raise_error(e)
        except NoResultFound as e:
            raise UserNotFoundError from e

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]

        if constraint == "ix__user__username":
            raise UserAlreadyExistsError from e

        raise LMSError from e
