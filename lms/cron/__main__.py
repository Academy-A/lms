import logging

from aiomisc import entrypoint

from lms.cron.args import parser
from lms.cron.deps import configure_cron_dependencies
from lms.cron.service import NotificationCronService

log = logging.getLogger(__name__)


def main() -> None:
    args = parser.parse_args()

    configure_cron_dependencies(args)

    services = [
        NotificationCronService(
            scheduler=args.scheduler,
        ),
    ]

    with entrypoint(
        *services,
        log_level=args.log_level,
        log_format=args.log_format,
        pool_size=args.pool_size,
        debug=args.debug,
    ) as loop:
        log.info("Services entrypoint started")
        loop.run_forever()


if __name__ == "__main__":
    main()
