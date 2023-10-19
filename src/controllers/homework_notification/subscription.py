from typing import ClassVar

from src.controllers.homework_notification.base import BaseNotification


class SubscriptionNotification(BaseNotification):
    regexp_setting: ClassVar[str] = "checking_regexp_"
    folder_ids_prefix_key: ClassVar[str] = "checking_by_subscription_folder_ids"
    autopilot_url_key: ClassVar[str] = "checking_by_subscription_autopilot_url"
