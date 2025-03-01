from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, kw_only=True, slots=True)
class AutopilotConfig:
    regular_notification_url: str = field(
        default_factory=lambda: environ["APP_AUTOPILOT_REGULAR_NOTIFICATION_URL"]
    )
    subscription_notification_url: str = field(
        default_factory=lambda: environ["APP_AUTOPILOT_SUBSCRIPTION_NOTIFICATION_URL"]
    )
    additional_notification_url: str = field(
        default_factory=lambda: environ["APP_AUTOPILOT_ADDITIONAL_NOTIFICATION_URL"]
    )
