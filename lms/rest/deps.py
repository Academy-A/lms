from argparse import Namespace
from collections.abc import AsyncGenerator, Callable

from aiomisc_dependency import dependency
from google_api_service_helper import GoogleDrive, GoogleSheets
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lms.clients.autopilot import AUTOPILOT_BASE_URL, Autopilot
from lms.clients.soho import SOHO_BASE_URL, Soho
from lms.clients.telegram import TELEGRAM_BASE_URL, Telegram
from lms.db.uow import UnitOfWork
from lms.db.utils import create_async_engine, create_async_session_factory
from lms.logic.distribute_homeworks import Distributor
from lms.utils.http import create_web_session
from lms.utils.settings import SettingStorage


def configure_dependencies(args: Namespace) -> None:
    @dependency
    async def engine() -> AsyncGenerator[AsyncEngine, None]:
        engine = create_async_engine(
            connection_uri=args.pg_dsn,
            pool_pre_ping=True,
        )
        yield engine
        await engine.dispose()

    @dependency
    async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_async_session_factory(engine=engine)

    @dependency
    async def autopilot() -> AsyncGenerator[Autopilot, None]:
        async with create_web_session() as session:
            yield Autopilot(
                url=AUTOPILOT_BASE_URL,
                session=session,
            )

    @dependency
    async def telegram() -> AsyncGenerator[Telegram, None]:
        async with create_web_session() as session:
            yield Telegram(
                session=session,
                url=TELEGRAM_BASE_URL,
                bot_token=args.telegram_bot_token,
                default_chat_id=args.telegram_chat_id,
                default_parse_mode=args.telegram_parse_mode,
            )

    @dependency
    async def soho() -> AsyncGenerator[Soho, None]:
        async with create_web_session() as session:
            yield Soho(
                url=SOHO_BASE_URL,
                session=session,
                auth_token=args.soho_api_token,
                client_name="Soho Client",
            )

    @dependency
    async def google_sheets() -> GoogleSheets:
        return GoogleSheets(google_keys=args.google_keys)

    @dependency
    async def google_drive() -> GoogleDrive:
        return GoogleDrive(google_keys=args.google_keys)

    @dependency
    async def get_distributor(
        session_factory: async_sessionmaker[AsyncSession],
        google_sheets: GoogleSheets,
        google_drive: GoogleDrive,
        soho: Soho,
    ) -> Callable:
        async def new_distributor() -> AsyncGenerator[Distributor, None]:
            async with UnitOfWork(sessionmaker=session_factory) as uow:
                yield Distributor(
                    uow=uow,
                    google_drive=google_drive,
                    google_sheets=google_sheets,
                    soho=soho,
                    settings=SettingStorage(uow=uow),
                )

        return new_distributor

    return
