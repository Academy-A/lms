from collections.abc import AsyncGenerator, Callable

from aiomisc_dependency import dependency
from google_api_service_helper import GoogleDrive, GoogleSheets
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lms.adapters.autopilot.client import AUTOPILOT_BASE_URL, Autopilot
from lms.adapters.db.uow import UnitOfWork
from lms.adapters.db.utils import create_async_engine, create_async_session_factory
from lms.adapters.soho.soho import SOHO_BASE_URL, Soho
from lms.adapters.telegram.telegram import TELEGRAM_BASE_URL, Telegram
from lms.logic.distribute_homeworks import Distributor
from lms.logic.enroll_student import Enroller
from lms.presentation.rest.config import Config
from lms.utils.http import create_web_session


def configure_dependencies(config: Config) -> None:  # noqa: C901
    @dependency
    async def engine() -> AsyncGenerator[AsyncEngine, None]:
        async with create_async_engine(
            connection_uri=config.db.dsn,
            pool_pre_ping=True,
        ) as engine:
            yield engine

    @dependency
    async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_async_session_factory(engine=engine)

    @dependency
    async def autopilot() -> AsyncGenerator[Autopilot, None]:
        async with create_web_session() as session:
            yield Autopilot(
                url=AUTOPILOT_BASE_URL,
                session=session,
                client_name="autopilot",
            )

    @dependency
    async def telegram() -> AsyncGenerator[Telegram, None]:
        async with create_web_session() as session:
            yield Telegram(
                session=session,
                url=TELEGRAM_BASE_URL,
                bot_token=config.telegram.bot_token,
                default_chat_id=config.telegram.chat_id,
                default_parse_mode=config.telegram.parse_mode,
                client_name="telegram",
            )

    @dependency
    async def soho() -> AsyncGenerator[Soho, None]:
        async with create_web_session() as session:
            yield Soho(
                url=SOHO_BASE_URL,
                session=session,
                auth_token=config.soho.token,
                client_name="Soho Client",
            )

    @dependency
    async def google_sheets() -> GoogleSheets:
        return GoogleSheets(google_keys=config.google.keys)

    @dependency
    async def google_drive() -> GoogleDrive:
        return GoogleDrive(google_keys=config.google.keys)

    @dependency
    async def get_distributor(
        session_factory: async_sessionmaker[AsyncSession],
        google_sheets: GoogleSheets,
        google_drive: GoogleDrive,
        soho: Soho,
    ) -> Callable:
        async def new_distributor() -> AsyncGenerator[Distributor, None]:
            uow = UnitOfWork(sessionmaker=session_factory)
            async with uow.start():
                yield Distributor(
                    uow=uow,
                    google_drive=google_drive,
                    google_sheets=google_sheets,
                    soho=soho,
                )

        return new_distributor

    @dependency
    async def enroller(
        session_factory: async_sessionmaker[AsyncSession],
        autopilot: Autopilot,
        telegram: Telegram,
    ) -> Enroller:
        return Enroller(
            uow=UnitOfWork(session_factory),
            autopilot=autopilot,
            telegram=telegram,
        )

    return
