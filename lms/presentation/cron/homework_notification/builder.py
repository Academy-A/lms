from collections.abc import AsyncGenerator, Callable, Sequence
from dataclasses import dataclass
from typing import Final

from google_api_service_helper import GoogleDrive
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.adapters.autopilot.client import Autopilot
from lms.adapters.db.uow import UnitOfWork
from lms.generals.models.subject import Subject
from lms.presentation.cron.homework_notification.additional import (
    AdditionalNotification,
)
from lms.presentation.cron.homework_notification.base import BaseNotification
from lms.presentation.cron.homework_notification.regular import RegularNotification
from lms.presentation.cron.homework_notification.subscription import (
    SubscriptionNotification,
)

RUSSIA_SUBJECT_ID: Final[int] = 1


@dataclass(frozen=True)
class NotificationBuilder:
    autopilot: Autopilot
    session_factory: async_sessionmaker[AsyncSession]
    google_drive: GoogleDrive
    regular_notification_url: str
    subscription_notification_url: str
    additional_notification_url: str

    async def build(self) -> AsyncGenerator[Callable, None]:
        async for callback in self._build_regular_notify_callbacks():
            yield callback

        async for callback in self._build_subscription_notify_callbacks():
            yield callback

        async for callback in self._build_additional_notify_callbacks():
            yield callback

    async def _build_regular_notify_callbacks(
        self,
    ) -> AsyncGenerator[Callable, None]:
        uow = UnitOfWork(self.session_factory)
        async with uow.start():
            subjects = await uow.subject.read_all()
            for subject in subjects:
                yield await self._build_notify_callback(
                    subject=subject,
                    autopilot_url=self.regular_notification_url,
                    folder_ids=subject.check_regular_nofitication_folder_ids,
                    notification_class=RegularNotification,
                )

    async def _build_subscription_notify_callbacks(
        self,
    ) -> AsyncGenerator[Callable, None]:
        uow = UnitOfWork(self.session_factory)
        async with uow.start():
            subject = await uow.subject.read_by_id(RUSSIA_SUBJECT_ID)
            yield await self._build_notify_callback(
                subject=subject,
                autopilot_url=self.subscription_notification_url,
                folder_ids=subject.check_subscription_notification_folder_ids,
                notification_class=SubscriptionNotification,
            )

    async def _build_additional_notify_callbacks(
        self,
    ) -> AsyncGenerator[Callable, None]:
        uow = UnitOfWork(self.session_factory)
        async with uow.start():
            subject = await uow.subject.read_by_id(RUSSIA_SUBJECT_ID)
            yield await self._build_notify_callback(
                subject=subject,
                autopilot_url=self.additional_notification_url,
                folder_ids=subject.check_additional_notification_folder_ids,
                notification_class=AdditionalNotification,
            )

    async def _build_notify_callback(
        self,
        subject: Subject,
        autopilot_url: str,
        folder_ids: Sequence[str],
        notification_class: type[BaseNotification],
    ) -> Callable:
        async def notify() -> None:
            uow = UnitOfWork(self.session_factory)
            async with uow.start():
                notification = notification_class(
                    autopilot=self.autopilot,
                    uow=uow,
                    google_drive=self.google_drive,
                    subject_id=subject.id,
                    subject_eng=subject.eng_name,
                    autopilot_url=autopilot_url,
                    regexp=subject.check_file_regex,
                    folder_ids=folder_ids,
                )
                await notification.notify()

        return notify
