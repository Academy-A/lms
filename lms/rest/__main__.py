import logging

from aiomisc import entrypoint
from aiomisc_log import basic_config

from lms.rest.args import Parser
from lms.rest.deps import configure_dependencies
from lms.rest.service import REST

log = logging.getLogger(__name__)


def main() -> None:
    parser = Parser(auto_env_var_prefix="APP_")
    parser.parse_args([])
    parser.sanitize_env()

    basic_config(
        level=parser.log.level,
        log_format=parser.log.format,
        buffered=False,
    )

    configure_dependencies(parser)

    services = [
        REST(
            host=parser.api.host,
            port=parser.api.port,
            debug=parser.debug,
            title=parser.api.title,
            description=parser.api.description,
            version=parser.api.version,
            secret_key=parser.security.secret_key,
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
