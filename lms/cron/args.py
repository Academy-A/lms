import argparse

import configargparse
from aiomisc_log import LogFormat, LogLevel

from lms.utils.args import load_google_keys

parser = configargparse.ArgumentParser(
    allow_abbrev=False,
    auto_env_var_prefix="APP_",
    description="Project LMS",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument("-D", "--debug", action="store_true")
parser.add_argument(
    "-s",
    "--pool-size",
    type=int,
    default=6,
    help="Thread pool size",
)

group = parser.add_argument_group("Logging options")
group.add_argument("--log-level", default=LogLevel.info, choices=LogLevel.choices())
group.add_argument("--log-format", choices=LogFormat.choices(), default=LogFormat.color)

group = parser.add_argument_group("PostgreSQL options")
group.add_argument("--pg-dsn", required=True, type=str)

group = parser.add_argument_group("Cron options")
group.add_argument("--scheduler", default="0/30 * * * *")

group = parser.add_argument_group("Google Keys")
group.add_argument("--google-keys", required=True, type=load_google_keys)

group = parser.add_argument_group("Autopilot URLs")
group.add_argument("--regular-notification-url", required=True, type=str)
group.add_argument("--subscription-notification-url", required=True, type=str)
group.add_argument("--additional-notification-url", required=True, type=str)
