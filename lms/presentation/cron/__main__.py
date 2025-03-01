import logging

from aiomisc import entrypoint

from lms.presentation.cron.config import Config
from lms.presentation.cron.deps import configure_cron_dependencies
from lms.presentation.cron.service import NotificationCronService

log = logging.getLogger(__name__)


def main() -> None:
    config = Config()

    configure_cron_dependencies(config=config)

    services = [
        NotificationCronService(
            scheduler=config.cron.scheduler,
        ),
    ]

    with entrypoint(
        *services,
        log_level=config.log.level,
        log_format=config.log.format,
        pool_size=config.app.pool_size,
        debug=config.app.debug,
    ) as loop:
        log.info("Services entrypoint started")
        loop.run_forever()


if __name__ == "__main__":
    main()
