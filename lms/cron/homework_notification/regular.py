from lms.cron.homework_notification.base import BaseNotification


class RegularNotification(BaseNotification):
    async def filter_parsed_files(self) -> None:
        self._filtered_files = []
        for file in self._parsed_files:
            if file.student_id is not None:
                self._filtered_files.append(file)
