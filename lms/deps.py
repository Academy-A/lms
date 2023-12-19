from argparse import Namespace
from collections.abc import AsyncGenerator

from aiomisc_dependency import dependency
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lms.clients.autopilot import AUTOPILOT_BASE_URL, Autopilot
from lms.clients.soho import SOHO_BASE_URL, Soho
from lms.clients.telegram import TELEGRAM_BASE_URL, Telegram
from lms.cron.homework_notification.builder import NotificationBuilder
from lms.db.utils import create_async_engine, create_async_session_factory
from lms.utils.http import create_web_session


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
    async def notification_builder(
        session_factory: async_sessionmaker[AsyncSession],
        autopilot: Autopilot,
    ) -> NotificationBuilder:
        return NotificationBuilder(
            autopilot=autopilot,
            session_factory=session_factory,
        )

    return
