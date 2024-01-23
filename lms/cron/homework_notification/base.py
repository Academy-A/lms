import abc
import asyncio
import logging
import re
from collections.abc import Sequence

from google_api_service_helper import GoogleDrive
from google_api_service_helper.drive.schemas import FileResponse

from lms.clients.autopilot import Autopilot
from lms.cron.homework_notification.utils import get_google_folder_files_recursively
from lms.db.uow import UnitOfWork
from lms.generals.models.parsed_file import ParsedFile

NOTIFICATION_TIME_PAUSE_SECONDS = 0.3

log = logging.getLogger(__name__)


class BaseNotification(abc.ABC):
    uow: UnitOfWork

    _google_drive: GoogleDrive
    _folder_ids: Sequence[str]
    _subject_id: int
    _autopilot: Autopilot

    def __init__(
        self,
        uow: UnitOfWork,
        autopilot: Autopilot,
        google_drive: GoogleDrive,
        subject_id: int,
        autopilot_url: str,
        regexp: str,
        folder_ids: Sequence[str],
    ) -> None:
        self.uow = uow
        self._subject_id = subject_id
        self._autopilot = autopilot
        self._autopilot_url = autopilot_url
        self._google_drive = google_drive
        self._folder_ids = folder_ids
        self._regexp = regexp

        self._new_files: list[FileResponse] = []
        self._parsed_files: list[ParsedFile] = []
        self._filtered_files: list[ParsedFile] = []

    async def notify(self) -> None:
        await self.get_new_files()
        await self.parse_file_names()
        await self.filter_parsed_files()
        await self.send_notificatons()
        await self.save_new_files()

    async def get_new_files(self) -> None:
        total_new_files = []
        for folder_id in self._folder_ids:
            folder_files = await get_google_folder_files_recursively(
                google_drive=self._google_drive,
                folder_id=folder_id,
            )
            new_files = []
            for file in folder_files:
                if await self.uow.file.get_by_google_drive_id(file.id):
                    continue
                else:
                    new_files.append(file)
            total_new_files.extend(new_files)
        self._new_files = total_new_files
        log.info(
            "%s subject_id=%s: total new files %s",
            self.__class__.__name__,
            self._subject_id,
            len(self._new_files),
        )

    async def parse_file_names(self) -> None:
        for file in self._new_files:
            result = re.match(self._regexp, file.name)
            if result is None:
                log.info(
                    "File ID %s error: file name does'nt match with pattern: %s",
                    file.id,
                    file.name,
                )
                continue
            vk_id, essay_number = int(result[1]), result[2]
            student = await self.uow.student.read_by_vk_id(vk_id=vk_id)
            if student is None:
                log.info(
                    "File ID %s error: student with VK ID: %s not found",
                    file.id,
                    vk_id,
                )
            self._parsed_files.append(
                ParsedFile(
                    id=file.id,
                    name=file.name,
                    url=file.webViewLink,
                    vk_id=vk_id,
                    essay_number=essay_number,
                    student_id=student.id if student else None,
                )
            )

    async def filter_parsed_files(self) -> None:
        self._filtered_files = self._parsed_files.copy()

    async def save_new_files(self) -> None:
        for file in self._filtered_files:
            log.info("save file %s", file)
            await self.uow.file.create(
                file_id=file.id,
                name=file.name,
                url=file.url,
                student_id=file.student_id,
                subject_id=self._subject_id,
            )
        await self.uow.commit()

    async def send_notificatons(self) -> None:
        for file in self._filtered_files:
            log.info("send file %s", file)
            await self._autopilot.send_homework(
                target_path=self._autopilot_url,
                student_vk_id=file.vk_id,
                file_url=file.url,
                title=file.essay_number,
            )
            await asyncio.sleep(NOTIFICATION_TIME_PAUSE_SECONDS)
