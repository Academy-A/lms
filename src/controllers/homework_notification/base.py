import abc
import re
import time

from loguru import logger
from sqlalchemy.orm import Session
from google_api_service_helper import GoogleDrive
from google_api_service_helper.drive.schemas import FileResponse

from src.controllers.homework_notification.dto import FileDTO
from src.db.models import Student, VerifiedWorkFile

NOTIFICATION_TIME_PAUSE_SECONDS = 0.3


class BaseNotification(abc.ABC):
    regexp_setting = "checking_regexp_"

    def __init__(
        self,
        session: Session,
        subject_id: int,
        autopilot_url: str,
        regexp: str,
        root_folder_ids: list[str],
        google_drive: GoogleDrive,
    ) -> None:
        self.new_files: list[FileResponse] = []
        self.parsed_files: list[FileDTO] = []
        self.session = session
        self.subject_id = subject_id
        self.autopilot_url = autopilot_url
        self.regexp = regexp
        self.google_drive = google_drive
        self.root_folder_ids = root_folder_ids

    def notify(self) -> None:
        self.get_new_files()
        self.parse_file_names()
        self.send_new_files_data()
        self.save_new_files()

    def get_new_files(self) -> None:
        for folder_id in self.root_folder_ids:
            new_files = []
            files = self.google_drive.get_all_folder_files_recursively(
                folder_id=folder_id
            )
            for file in files:
                if self.read_file_by_id(file.id):
                    continue

                new_files.append(file)
            self.new_files.extend(new_files)
        logger.info("Total new files {count}", count=len(self.new_files))

    def read_file_by_id(self, file_id: str) -> VerifiedWorkFile | None:
        return self.session.query(VerifiedWorkFile).filter_by(file_id=file_id).first()

    def save_file(self, file: FileDTO) -> None:
        self.session.add(
            VerifiedWorkFile(  # type: ignore[call-arg]
                file_id=file.id,
                name=file.name,
                url=file.url,
                student_id=file.student_id,
                subject_id=self.subject_id,
            )
        )
        self.session.commit()

    def parse_file_names(self) -> None:
        for file in self.new_files:
            result = re.match(self.regexp, file.name)
            if result is None:
                logger.info(
                    "File ID {file_id} error: file name does'nt match with pattern",
                    file_id=file.id,
                )
                continue
            vk_id, essay_number = int(result[1]), result[2]
            student = self.session.query(Student).filter_by(vk_id=vk_id).first()
            if student is None:
                logger.info(
                    "File ID {file_id} error: student with VK ID: {vk_id} not found",
                    file_id=file.id,
                    vk_id=vk_id,
                )
                continue
            self.parsed_files.append(
                FileDTO(
                    id=file.id,
                    name=file.name,
                    url=file.webViewLink,
                    vk_id=vk_id,
                    essay_number=essay_number,
                    student_id=student.id,
                )
            )

    def save_new_files(self) -> None:
        for file in self.parsed_files:
            if file.vk_id is None:
                continue
            logger.info("save_new_files_")
            # self.save_file(file)

    def send_new_files_data(self) -> None:
        for file in self.parsed_files:
            if file.vk_id is None:
                continue
            logger.info("send_new_files_data")
            # httpx.get(self.autopilot_url, params=file.get_send_params())
            time.sleep(NOTIFICATION_TIME_PAUSE_SECONDS)
