import logging

from aiomisc.service.cron import CronService

from lms.cron.homework_notification.builder import NotificationBuilder

log = logging.getLogger(__name__)


class NotificationCronService(CronService):
    __required__ = ("scheduler",)
    __dependencies__ = ("notification_builder",)

    scheduler: str

    notification_builder: NotificationBuilder

    async def start(self) -> None:
        async for notify in self.notification_builder.build():
            self.register(notify, spec=self.scheduler)
            log.info("Cron notification was registered")
        await super().start()
