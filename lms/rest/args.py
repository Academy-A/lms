import argclass

from lms.domains.args import (
    APIGroup,
    DatabaseGroup,
    GoogleGroup,
    LogGroup,
    SecurityGroup,
    SohoGroup,
    TelegramGroup,
)


class Parser(argclass.Parser):
    debug: bool = argclass.Argument(
        "-D",
        "--debug",
        default=False,
        type=lambda x: x.lower() == "true",
    )
    pool_size: int = argclass.Argument(
        "-s", "--pool-size", type=int, default=4, help="Thread pool size"
    )
    log = LogGroup(title="Logging options")
    api = APIGroup(title="HTTP options")
    db = DatabaseGroup(title="Database options")
    security = SecurityGroup(title="Security options")
    telegram = TelegramGroup(title="Telegram options")
    soho = SohoGroup(title="Soho options")
    google = GoogleGroup(title="Google options")
