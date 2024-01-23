import logging

from aiomisc import entrypoint
from aiomisc_log import basic_config

from lms.rest.args import parser
from lms.rest.deps import configure_dependencies
from lms.rest.service import REST

log = logging.getLogger(__name__)


def main() -> None:
    args = parser.parse_args()

    basic_config(
        level=args.log_level,
        log_format=args.log_format,
        buffered=False,
    )

    configure_dependencies(args)

    services = [
        REST(
            host=args.api_address,
            port=args.api_port,
            debug=args.debug,
            project_name=args.project_name,
            project_description=args.project_description,
            project_version=args.project_version,
            secret_key=args.api_secret_key,
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
