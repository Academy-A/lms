from collections.abc import AsyncGenerator, Callable

import orjson
from google_api_service_helper import GoogleDrive, GoogleKeys
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.clients.autopilot import Autopilot
from lms.cron.homework_notification.base import BaseNotification
from lms.cron.homework_notification.regular import RegularNotification
from lms.cron.homework_notification.subscription import SubscriptionNotification
from lms.cron.homework_notification.utils import get_cleaned_folder_ids
from lms.db.uow import UnitOfWork
from lms.utils.settings import SettingStorage

GOOLGLE_KEYS = "google_keys"


class NotificationBuilder:
    _autopilot: Autopilot
    _uow: UnitOfWork
    _session_factroy: async_sessionmaker[AsyncSession]

    def __init__(
        self, autopilot: Autopilot, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self._autopilot = autopilot
        self._session_factory = session_factory
        self._uow = UnitOfWork(session_factory)

    async def build(self) -> AsyncGenerator[Callable, None]:
        async for callback in self._build_regular_notify_callbacks():
            yield callback

        async for callback in self._build_subscription_notify_callbacks():
            yield callback

    async def _build_regular_notify_callbacks(
        self,
    ) -> AsyncGenerator[Callable, None]:
        async with self._uow:
            subjects = await self._uow.subject.read_all()
            for subject in subjects:
                yield await self._build_notify_callback(
                    subject_id=subject.id,
                    subject_eng_name=subject.eng_name,
                    notification_class=RegularNotification,
                )

    async def _build_subscription_notify_callbacks(
        self,
    ) -> AsyncGenerator[Callable, None]:
        async with self._uow:
            subject = await self._uow.subject.read_by_id(1)
            yield await self._build_notify_callback(
                subject_id=subject.id,
                subject_eng_name=subject.eng_name,
                notification_class=SubscriptionNotification,
            )

    async def _build_notify_callback(
        self,
        subject_id: int,
        subject_eng_name: str,
        notification_class: type[BaseNotification],
    ) -> Callable:
        async def notify() -> None:
            local_uow = UnitOfWork(self._session_factory)
            settings = SettingStorage(uow=local_uow)
            async with local_uow:
                autopilot_url = await settings.get(notification_class.autopilot_url_key)
                google_keys = await settings.get(GOOLGLE_KEYS)
                google_drive = GoogleDrive(
                    google_keys=GoogleKeys(**orjson.loads(google_keys))
                )
                folder_ids_key = notification_class.folder_ids_prefix + subject_eng_name
                folder_ids_str = await settings.get(folder_ids_key)
                folder_ids = get_cleaned_folder_ids(folder_ids_str)
                regexp = await settings.get(
                    notification_class.regexp_setting + subject_eng_name
                )

                notification = notification_class(
                    autopilot=self._autopilot,
                    uow=local_uow,
                    subject_id=subject_id,
                    autopilot_url=autopilot_url,
                    regexp=regexp,
                    folder_ids=folder_ids,
                    google_drive=google_drive,
                )
                await notification.notify()

        return notify
