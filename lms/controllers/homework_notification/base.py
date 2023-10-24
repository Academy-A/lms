import abc
import logging
import re
import time
from typing import ClassVar

import httpx
import orjson
from google_api_service_helper import GoogleDrive, GoogleKeys
from google_api_service_helper.drive.schemas import FileResponse
from pyparsing import Any
from sqlalchemy.orm import Session

from lms.controllers.homework_notification.dto import FileDTO
from lms.controllers.homework_notification.utils import get_cleaned_folder_ids
from lms.db.models import Student, VerifiedWorkFile
from lms.utils import get_setting

NOTIFICATION_TIME_PAUSE_SECONDS = 0.3

log = logging.getLogger(__name__)


class BaseNotification(abc.ABC):
    regexp_setting: ClassVar[str] = "checking_regexp_"
    folder_ids_prefix: ClassVar[str]
    autopilot_url_key: ClassVar[str]

    _session: Session
    _google_drive: GoogleDrive
    _folder_ids: list[str]
    _subject_id: int

    def __init__(
        self,
        session: Session,
        subject_id: int,
        subject_eng_name: str,
    ) -> None:
        self.new_files: list[FileResponse] = []
        self.parsed_files: list[FileDTO] = []
        self.filtered_files: list[FileDTO] = []
        self._session = session
        self._subject_id = subject_id
        self._subject_eng_name = subject_eng_name

    def init(self) -> None:
        google_keys = get_setting(self._session, "google_keys")
        self._google_drive = GoogleDrive(
            google_keys=GoogleKeys(**orjson.loads(google_keys))
        )
        folder_ids_key = self.folder_ids_prefix + self._subject_eng_name
        folder_ids = get_setting(session=self._session, key=folder_ids_key)
        self._folder_ids = get_cleaned_folder_ids(folder_ids)
        self._autopilot_url = get_setting(
            key=self.autopilot_url_key,
            session=self._session,
        )
        regexp_key = self.regexp_setting + self._subject_eng_name
        self._regexp = get_setting(session=self._session, key=regexp_key)

    def notify(self) -> None:
        self.get_new_files()
        self.parse_file_names()
        self.filter_parsed_files()
        self.send_new_files_data()
        self.save_new_files()

    def get_new_files(self) -> None:
        for folder_id in self._folder_ids:
            new_files = []
            files = self._google_drive.get_all_folder_files_recursively(
                folder_id=folder_id
            )
            for file in files:
                if self.read_file_by_id(file.id):
                    continue

                new_files.append(file)
            self.new_files.extend(new_files)
        log.info("Total new files %s", len(self.new_files))
        raise Exception

    def read_file_by_id(self, file_id: str) -> VerifiedWorkFile | None:
        return self._session.query(VerifiedWorkFile).filter_by(file_id=file_id).first()

    def save_file(self, file: FileDTO) -> None:
        self._session.add(
            VerifiedWorkFile(  # type: ignore[call-arg]
                file_id=file.id,
                name=file.name,
                url=file.url,
                student_id=file.student_id,
                subject_id=self._subject_id,
            )
        )
        self._session.commit()

    def parse_file_names(self) -> None:
        for file in self.new_files:
            result = re.match(self._regexp, file.name)
            if result is None:
                log.info(
                    "File ID %s error: file name does'nt match with pattern",
                    file.id,
                )
                continue
            vk_id, essay_number = int(result[1]), result[2]
            student = self.get_student_by_vk_id(vk_id)
            if student is None:
                log.info(
                    "File ID %s error: student with VK ID: %s not found",
                    file.id,
                    vk_id,
                )
            self.parsed_files.append(
                FileDTO(
                    id=file.id,
                    name=file.name,
                    url=file.webViewLink,
                    vk_id=vk_id,
                    essay_number=essay_number,
                    student_id=student.id if student else None,
                )
            )

    def filter_parsed_files(self) -> None:
        self.filtered_files = self.parsed_files.copy()

    def save_new_files(self) -> None:
        for file in self.filtered_files:
            log.info("save file %s", file)
            self.save_file(file)

    def get_student_by_vk_id(self, vk_id: int) -> Student | None:
        return self._session.query(Student).filter_by(vk_id=vk_id).first()

    def send_new_files_data(self) -> None:
        for file in self.filtered_files:
            log.info("send file %s", file)
            httpx.get(self._autopilot_url, params=self.get_send_params(file))
            time.sleep(NOTIFICATION_TIME_PAUSE_SECONDS)

    @staticmethod
    def get_send_params(file: FileDTO) -> dict[str, Any]:
        return {
            "avtp": 1,
            "sid": file.vk_id,
            "soch": file.url,
            "title": file.essay_number,
        }
