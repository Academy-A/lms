import logging

from aiomisc_log import LogFormat, LogLevel, basic_config
from configargparse import ArgParser
from pydantic import BaseModel, PositiveInt, PostgresDsn

log = logging.getLogger(__name__)


class RunDistributionSchema(BaseModel):
    pg_dsn: PostgresDsn

    product_id: PositiveInt
    name: str
    homework_ids: list[PositiveInt]


def get_parser() -> ArgParser:
    parser = ArgParser()
    parser.add_argument("--pg-dsn", required=True, type=str)
    parser.add_argument("--product-id", required=True, type=int)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--homework-ids", nargs="+", type=int, required=True)
    group = parser.add_argument_group("Logging options")
    group.add_argument("--log-level", default=LogLevel.info, choices=LogLevel.choices())
    group.add_argument(
        "--log-format", choices=LogFormat.choices(), default=LogFormat.color
    )
    return parser


async def amain(
    pg_dsn: PostgresDsn,
    product_id: int,
    name: str,
    homework_ids: list[int],
) -> None:
    pass


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    basic_config(level=args.log_level, log_format=args.log_format)
    RunDistributionSchema.model_validate(args, from_attributes=True).model_dump()


if __name__ == "__main__":
    main()
