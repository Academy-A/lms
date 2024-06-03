import logging

from aiomisc import entrypoint

from lms.cron.args import Parser
from lms.cron.deps import configure_cron_dependencies
from lms.cron.service import NotificationCronService

log = logging.getLogger(__name__)


def main() -> None:
    parser = Parser(auto_env_var_prefix="APP_")
    parser.parse_args([])
    parser.sanitize_env()

    configure_cron_dependencies(parser)

    services = [
        NotificationCronService(
            scheduler=parser.cron.scheduler,
        ),
    ]

    with entrypoint(
        *services,
        log_level=parser.log.level,
        log_format=parser.log.format,
        pool_size=parser.pool_size,
        debug=parser.debug,
    ) as loop:
        log.info("Services entrypoint started")
        loop.run_forever()


if __name__ == "__main__":
    main()
