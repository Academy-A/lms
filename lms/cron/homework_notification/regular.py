from typing import ClassVar

from lms.cron.homework_notification.base import BaseNotification


class RegularNotification(BaseNotification):
    regexp_setting: ClassVar[str] = "checking_regexp_"
    folder_ids_prefix: ClassVar[str] = "regular_notification_folder_ids_"
    autopilot_url_key: ClassVar[str] = "regular_notification_autopilot_url"

    async def filter_parsed_files(self) -> None:
        self._filtered_files = []
        for file in self._parsed_files:
            if file.student_id is not None:
                self._filtered_files.append(file)
