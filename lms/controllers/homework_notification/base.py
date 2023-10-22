import abc
import re
import time
from typing import ClassVar

import httpx
import orjson
from google_api_service_helper import GoogleDrive, GoogleKeys
from google_api_service_helper.drive.schemas import FileResponse
from loguru import logger
from pyparsing import Any
from sqlalchemy.orm import Session

from lms.controllers.homework_notification.dto import FileDTO
from lms.controllers.homework_notification.utils import get_cleaned_folder_ids
from lms.db.models import Setting, Student, VerifiedWorkFile

NOTIFICATION_TIME_PAUSE_SECONDS = 0.3


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
        google_keys = get_settings(self._session, "google_keys")
        if google_keys is None:
            raise ValueError("Google Keys not loaded!")
        self._google_drive = GoogleDrive(
            google_keys=GoogleKeys(**orjson.loads(google_keys))
        )
        folder_ids_key = self.folder_ids_prefix + self._subject_eng_name
        folder_ids = get_settings(session=self._session, key=folder_ids_key)
        if folder_ids is None:
            raise ValueError(f"Folder IDs on key `{folder_ids_key}` not loaded")
        self._folder_ids = get_cleaned_folder_ids(folder_ids)
        self._autopilot_url = get_settings(
            key=self.autopilot_url_key,
            session=self._session,
        )
        if self._autopilot_url is None:
            raise ValueError("Autopilot url not loaded")
        regexp_key = self.regexp_setting + self._subject_eng_name
        self._regexp = get_settings(session=self._session, key=regexp_key)
        if self._regexp is None:
            raise ValueError(f"Regexp on key `{regexp_key}` not loaded")

    def notify(self) -> None:
        self.get_new_files()
        self.parse_file_names()
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
        logger.info("Total new files {count}", count=len(self.new_files))

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
                logger.info(
                    "File ID {file_id} error: file name does'nt match with pattern",
                    file_id=file.id,
                )
                continue
            vk_id, essay_number = int(result[1]), result[2]
            student = self.get_student_by_vk_id(vk_id)
            if student is None:
                logger.info(
                    "File ID {file_id} error: student with VK ID: {vk_id} not found",
                    file_id=file.id,
                    vk_id=vk_id,
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
            logger.info("save file {file}", file=file)
            self.save_file(file)

    def get_student_by_vk_id(self, vk_id: int) -> Student | None:
        return self._session.query(Student).filter_by(vk_id=vk_id).first()

    def send_new_files_data(self) -> None:
        for file in self.filtered_files:
            logger.info("send file {file}", file=file)
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


def get_settings(session: Session, key: str, default: str | None = None) -> str:
    setting = session.query(Setting).filter_by(key=key).first()
    if setting is None and default is None:
        raise KeyError(f"{key} not in table Setting")
    return str(getattr(setting, "value", default))
