from src.controllers.homework_notification.base import BaseNotification


class RegularNotification(BaseNotification):
    folder_ids_prefix = "regular_notification_folder_ids_"
    autopilot_url_key = "regular_notification_autopilot_url"
