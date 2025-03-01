import logging

from aiomisc import entrypoint
from aiomisc_log import basic_config

from lms.presentation.rest.config import Config
from lms.presentation.rest.deps import configure_dependencies
from lms.presentation.rest.service import REST

log = logging.getLogger(__name__)


def main() -> None:
    config = Config()

    basic_config(
        level=config.log.level,
        log_format=config.log.format,
        buffered=False,
    )

    configure_dependencies(config)

    services = [
        REST(
            host=config.http.host,
            port=config.http.port,
            debug=config.app.debug,
            title=config.http.title,
            description=config.http.description,
            version=config.http.version,
            secret_key=config.security.secret_key,
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
