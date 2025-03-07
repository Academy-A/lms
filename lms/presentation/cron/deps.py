from collections.abc import AsyncGenerator

from aiomisc_dependency import dependency
from google_api_service_helper import GoogleDrive
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lms.adapters.autopilot.client import AUTOPILOT_BASE_URL, Autopilot
from lms.adapters.db.utils import create_async_engine, create_async_session_factory
from lms.presentation.cron.config import Config
from lms.presentation.cron.homework_notification.builder import NotificationBuilder
from lms.utils.http import create_web_session


def configure_cron_dependencies(config: Config) -> None:
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
    async def google_drive() -> GoogleDrive:
        return GoogleDrive(google_keys=config.google.keys)

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
            regular_notification_url=config.autopilot.regular_notification_url,
            subscription_notification_url=config.autopilot.subscription_notification_url,
            additional_notification_url=config.autopilot.additional_notification_url,
        )
