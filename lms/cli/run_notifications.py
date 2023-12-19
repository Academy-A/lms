import argparse
import asyncio
import logging

from aiomisc_log import LogFormat, LogLevel, basic_config
from configargparse import ArgParser
from pydantic import BaseModel, PostgresDsn

from lms.clients.autopilot import AUTOPILOT_BASE_URL, Autopilot
from lms.cron.homework_notification.builder import NotificationBuilder
from lms.db.utils import (
    create_async_engine,
    create_async_session_factory,
)
from lms.utils.http import create_web_session

log = logging.getLogger(__name__)


class RunNotificationSchema(BaseModel):
    pg_dsn: PostgresDsn

    regular: bool
    subscription: bool


def get_parser() -> ArgParser:
    parser = ArgParser(
        allow_abbrev=False,
        auto_env_var_prefix="APP_",
        description="Project LMS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--pg-dsn", required=True, type=str)

    group = parser.add_argument_group("Logging options")
    group.add_argument("--log-level", default=LogLevel.info, choices=LogLevel.choices())
    group.add_argument(
        "--log-format", choices=LogFormat.choices(), default=LogFormat.color
    )

    parser.add_argument("--regular", action="store_true")
    parser.add_argument("--subscription", action="store_true")

    return parser


async def amain(pg_dsn: PostgresDsn, regular: bool, subscription: bool) -> None:
    engine = create_async_engine(connection_uri=str(pg_dsn))
    session_factory = create_async_session_factory(engine)
    async with create_web_session() as session:
        autopilot = Autopilot(
            url=AUTOPILOT_BASE_URL,
            session=session,
        )
        builder = NotificationBuilder(
            session_factory=session_factory,
            autopilot=autopilot,
        )
        log.info("Start notifications")
        if regular:
            log.info("Run regular notifications")
            async for notify in builder._build_regular_notify_callbacks():
                await notify()

        if subscription:
            log.info("Run subscription notifications")
            async for notify in builder._build_subscription_notify_callbacks():
                await notify()
        log.info("End notification")


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    basic_config(level=args.log_level, log_format=args.log_format)

    data = RunNotificationSchema.model_validate(args, from_attributes=True).model_dump()
    asyncio.run(amain(**data))


if __name__ == "__main__":
    main()
