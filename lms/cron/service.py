import orjson
from aiomisc.service.cron import CronService
from google_api_service_helper import GoogleDrive, GoogleKeys
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.cron.homework_notification.base import BaseNotification
from lms.cron.homework_notification.regular import RegularNotification
from lms.cron.homework_notification.subscription import SubscriptionNotification
from lms.cron.homework_notification.utils import get_cleaned_folder_ids
from lms.db.uow import UnitOfWork

GOOLGLE_KEYS = "google_keys"


class LMSCronService(CronService):
    __required__ = ("scheduler",)
    __dependencies__ = ("session_factory", "uow")

    scheduler: str

    uow: UnitOfWork
    session_factory: async_sessionmaker[AsyncSession]

    async def start(self) -> None:
        await self._register_regular_notifications()
        await self._register_subscription_notifications()
        await super().start()

    async def _register_regular_notifications(self) -> None:
        async with self.uow:
            subjects = await self.uow.subject.read_all()
            for subject in subjects:
                await self._register_notification(
                    subject_id=subject.id,
                    subject_eng_name=subject.eng_name,
                    notification_class=RegularNotification,
                )

    async def _register_subscription_notifications(self) -> None:
        async with self.uow:
            subject = await self.uow.subject.read_by_id(1)
            await self._register_notification(
                subject_id=subject.id,
                subject_eng_name=subject.eng_name,
                notification_class=SubscriptionNotification,
            )

    async def _register_notification(
        self,
        subject_id: int,
        subject_eng_name: str,
        notification_class: type[BaseNotification],
    ) -> None:
        async def notify() -> None:
            local_uow = UnitOfWork(self.session_factory)
            async with local_uow:
                autopilot_url = await local_uow.setting.get(
                    notification_class.autopilot_url_key
                )
                google_keys = await local_uow.setting.get(GOOLGLE_KEYS)
                google_drive = GoogleDrive(
                    google_keys=GoogleKeys(**orjson.loads(google_keys))
                )
                folder_ids_key = notification_class.folder_ids_prefix + subject_eng_name
                folder_ids_str = await local_uow.setting.get(folder_ids_key)
                folder_ids = get_cleaned_folder_ids(folder_ids_str)
                regexp = await local_uow.setting.get(
                    notification_class.regexp_setting + subject_eng_name
                )

                notification = notification_class(
                    uow=local_uow,
                    subject_id=subject_id,
                    autopilot_url=autopilot_url,
                    regexp=regexp,
                    folder_ids=folder_ids,
                    google_drive=google_drive,
                )
                await notification.notify()

        self.register(notify, spec=self.scheduler)
        return
