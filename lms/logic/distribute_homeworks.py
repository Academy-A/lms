from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from aiomisc import threaded
from google_api_service_helper import GoogleDrive, GoogleSheets

from lms.clients.soho import Soho, SohoHomework
from lms.db.repositories.student_product import StudentDistributeData
from lms.db.uow import UnitOfWork
from lms.generals.enums import DistributionErrorMessage
from lms.generals.models.distribution import DistributionParams
from lms.generals.models.subject import Subject
from lms.utils.distribution.models import (
    Distribution,
    DistributionReviewer,
    ErrorHomework,
    StudentHomework,
)
from lms.utils.settings import SettingStorage

SHEET_INDEX = 4
SHEET_MAJOR_DIMENSION = "COLUMNS"


@dataclass(frozen=True, slots=True)
class Distributor:
    settings: SettingStorage
    uow: UnitOfWork
    google_sheets: GoogleSheets
    google_drive: GoogleDrive
    soho: Soho

    async def make_distribution(
        self,
        params: DistributionParams,
        created_at: datetime,
    ) -> None:
        homeworks = await self._get_soho_homeworks(params.homework_ids)
        subject = await self._get_subject(params.product_ids[0])
        reviewers = await self._get_reviewers(subject_id=subject.id)
        student_data = await self._get_students_data(
            subject_id=subject.id,
            homeworks=homeworks,
        )
        filtered_homeworks, error_homeworks = await self._filter_homeworks(
            homeworks=homeworks,
            student_data=student_data,
        )
        distribution = Distribution(
            created_at=created_at,
            params=params,
            homeworks=homeworks,
            filtered_homeworks=filtered_homeworks,
            error_homeworks=error_homeworks,
            reviewers=reviewers,
        )
        await distribution.distribute()
        new_folder_id = await self._create_folder_for_homeworks(
            parent_folder_id=subject.check_drive_foler_id,
            distribution=distribution,
        )
        distribution.new_folder_id = new_folder_id
        await self._write_data_in_new_sheet(
            spreadsheet_id=subject.check_spreadsheet_id,
            distribution=distribution,
        )
        await self._save_distribution(
            subject_id=subject.id,
            distribution=distribution,
        )
        await self._add_folder_to_notification(
            subject_id=subject.id,
            folder_id=new_folder_id,
        )
        await self.uow.commit()

    async def _get_soho_homeworks(
        self,
        homework_ids: Sequence[int],
    ) -> Sequence[SohoHomework]:
        homeworks: list[SohoHomework] = []
        for homework_id in homework_ids:
            response = await self.soho.homeworks(homework_id)
            homeworks.extend(response.homeworks)
        return homeworks

    async def _get_subject(self, product_id: int) -> Subject:
        product = await self.uow.product.read_by_id(product_id=product_id)
        return await self.uow.subject.read_by_id(product.subject_id)

    async def _get_reviewers(self, subject_id: int) -> Sequence[DistributionReviewer]:
        reviewers = await self.uow.reviewer.get_by_subject_id(subject_id)
        return [DistributionReviewer(**r.model_dump()) for r in reviewers]

    async def _get_students_data(
        self,
        subject_id: int,
        homeworks: Sequence[SohoHomework],
    ) -> Sequence[StudentDistributeData]:
        vk_ids = set(hw.student_vk_id for hw in homeworks if hw.student_vk_id)
        return await self.uow.student_product.distribute_data(
            subject_id=subject_id,
            vk_ids=vk_ids,
        )

    async def _filter_homeworks(
        self,
        student_data: Sequence[StudentDistributeData],
        homeworks: Sequence[SohoHomework],
    ) -> tuple[Sequence[StudentHomework], Sequence[ErrorHomework]]:
        pre_filtered_homeworks: list[StudentHomework] = list()
        error_homeworks: list[ErrorHomework] = list()
        student_map = {st.vk_id: st for st in student_data}
        for hw in homeworks:
            if hw.student_vk_id is None:
                error_homeworks.append(
                    ErrorHomework(
                        homework=hw,
                        error_message=DistributionErrorMessage.HOMEWORK_WITHOUT_VK_ID,
                    )
                )
            elif hw.student_vk_id not in student_map:
                error_homeworks.append(
                    ErrorHomework(
                        homework=hw,
                        error_message=DistributionErrorMessage.STUDENT_WITH_VK_ID_NOT_FOUND,
                    )
                )
            elif student_map[hw.student_vk_id].is_expulsed:
                error_homeworks.append(
                    ErrorHomework(
                        homework=hw,
                        error_message=DistributionErrorMessage.STUDENT_WAS_EXPULSED,
                    )
                )
            else:
                pre_filtered_homeworks.append(
                    StudentHomework(
                        student_name=student_map[hw.student_vk_id].name,
                        student_vk_id=student_map[hw.student_vk_id].vk_id,
                        student_soho_id=hw.student_soho_id,
                        submission_url=hw.chat_url,
                        teacher_product_id=student_map[
                            hw.student_vk_id
                        ].teacher_product_id,
                    )
                )
        return pre_filtered_homeworks, error_homeworks

    async def _add_folder_to_notification(
        self, subject_id: int, folder_id: str
    ) -> None:
        subject = await self.uow.subject.read_by_id(subject_id=subject_id)
        subject.check_regular_nofitication_folder_ids
        if len(subject.check_regular_nofitication_folder_ids) >= 20:
            del subject.properties.check_regular_notification_folder_ids[0]
        subject.properties.check_regular_notification_folder_ids.append(folder_id)
        subj_dict = subject.model_dump()
        subj_dict["properties"] = subject.properties.model_dump(mode="json")
        await self.uow.subject.update(
            id_=subject.id,
            **subj_dict,
        )

    async def _save_distribution(
        self,
        subject_id: int,
        distribution: Distribution,
    ) -> None:
        data = distribution.model_dump()
        await self.uow.distribution.create(
            subject_id=subject_id,
            data=data,
        )

    @threaded
    def _create_folder_for_homeworks(
        self,
        distribution: Distribution,
        parent_folder_id: str,
    ) -> str:
        new_folder = self.google_drive.make_new_folder(
            new_folder_title=distribution.folder_title,
            parent_folder_id=parent_folder_id,
        )
        if new_folder is None:
            raise ValueError("Folder not created")
        self.google_drive.set_permissions_for_anyone(folder_id=new_folder.id)
        return new_folder.id

    @threaded
    def _write_data_in_new_sheet(
        self,
        distribution: Distribution,
        spreadsheet_id: str,
    ) -> None:
        self.google_sheets.create_sheet(
            spreadsheet_id=spreadsheet_id,
            title=distribution.sheet_title,
            index=SHEET_INDEX,
        )
        self.google_sheets.set_data(
            spreadsheet_id=spreadsheet_id,
            range_sheet=distribution.sheet_title,
            values=distribution.serialize_for_sheet(),
            major_dimension=SHEET_MAJOR_DIMENSION,
        )
