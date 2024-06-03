import argclass

from lms.domains.args import (
    AutopilotGroup,
    CronGroup,
    DatabaseGroup,
    GoogleGroup,
    LogGroup,
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
    cron = CronGroup(title="Cron options")
    autopilot = AutopilotGroup(title="Autopilot options")
    db = DatabaseGroup(title="Database options")
    google = GoogleGroup(title="Google options")
