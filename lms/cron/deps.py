from argparse import Namespace
from collections.abc import AsyncGenerator

from aiomisc_dependency import dependency
from google_api_service_helper import GoogleDrive
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lms.clients.autopilot import AUTOPILOT_BASE_URL, Autopilot
from lms.cron.homework_notification.builder import NotificationBuilder
from lms.db.utils import create_async_engine, create_async_session_factory
from lms.utils.http import create_web_session


def configure_cron_dependencies(args: Namespace) -> None:
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
    async def google_drive() -> GoogleDrive:
        return GoogleDrive(google_keys=args.google_keys)

    @dependency
    async def notification_builder(
        session_factory: async_sessionmaker[AsyncSession],
        autopilot: Autopilot,
        google_drive: GoogleDrive,
    ) -> NotificationBuilder:
        return NotificationBuilder(
            autopilot=autopilot,
            session_factory=session_factory,
            google_drive=google_drive,
            regular_notification_url=args.regular_notification_url,
            subscription_notification_url=args.subscription_notification_url,
        )
