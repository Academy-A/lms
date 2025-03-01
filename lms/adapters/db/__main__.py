import argparse
import logging

from alembic.config import CommandLine

from lms.adapters.db.config import DatabaseConfig
from lms.adapters.db.utils import make_alembic_config


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    options = alembic.parser.parse_args()

    db_config = DatabaseConfig()

    if "cmd" not in options:
        alembic.parser.error("Too few arguments")
        exit(128)
    else:
        config = make_alembic_config(options, dsn=db_config.dsn)
        alembic.run_cmd(config, options)
        exit()


if __name__ == "__main__":
    main()
