import argparse
import asyncio
import logging
from typing import Annotated

from aiomisc_log import LogFormat, LogLevel, basic_config
from configargparse import ArgParser
from pydantic import BaseModel, PostgresDsn, SecretStr, StringConstraints
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.repositories.user import UserRepository
from lms.db.utils import create_async_engine
from lms.exceptions.user import UserNotFoundError
from lms.utils.password import get_password_hash

log = logging.getLogger(__name__)


class CreateUserSchema(BaseModel):
    username: Annotated[str, StringConstraints(min_length=8)]
    password: Annotated[SecretStr, StringConstraints(min_length=8)]
    pg_dsn: PostgresDsn


def get_parser() -> ArgParser:
    parser = ArgParser(
        allow_abbrev=False,
        auto_env_var_prefix="APP_",
        description="Project LMS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--pg-dsn", required=True, type=str)
    parser.add_argument(
        "--username",
        required=True,
        type=str,
    )
    parser.add_argument("--password", required=True, type=str)
    group = parser.add_argument_group("Logging options")
    group.add_argument("--log-level", default=LogLevel.info, choices=LogLevel.choices())
    group.add_argument(
        "--log-format", choices=LogFormat.choices(), default=LogFormat.color
    )

    return parser


async def create_user(
    session: AsyncSession, username: str, password: SecretStr
) -> None:
    user_repo = UserRepository(session)
    log.info("Trying update userdf %s", username)
    hashed_password = get_password_hash(password.get_secret_value())
    try:
        await user_repo.update_password_by_username(
            username=username,
            hashed_password=hashed_password,
        )
        await session.commit()
        log.info("Password for user %s was changed", username)
    except UserNotFoundError:
        log.warning("User %s not found", username)


async def amain(username: str, password: SecretStr, pg_dsn: PostgresDsn) -> None:
    engine = create_async_engine(connection_uri=str(pg_dsn))
    async with AsyncSession(engine) as session:
        await create_user(session=session, username=username, password=password)
    await engine.dispose()


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    basic_config(level=args.log_level, log_format=args.log_format)

    data = CreateUserSchema.model_validate(args, from_attributes=True).model_dump()
    asyncio.run(amain(**data))


if __name__ == "__main__":
    main()
