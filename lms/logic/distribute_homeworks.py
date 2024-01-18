from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from aiomisc import threaded
from google_api_service_helper import GoogleDrive, GoogleSheets

from lms.clients.soho import Soho, SohoHomework
from lms.cron.homework_notification.utils import get_cleaned_folder_ids
from lms.db.repositories.student_product import StudentDistributeData
from lms.db.uow import UnitOfWork
from lms.generals.models.distribution import DistributionParams
from lms.generals.models.subject import Subject
from lms.utils.distribution.models import Distribution, DistributionReviewer
from lms.utils.distribution.utils import NameGen
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

    async def make_distribution(self, params: DistributionParams) -> None:
        homeworks = await self._get_soho_homeworks(params.homework_ids)
        subject = await self._get_subject(params.product_ids[0])
        reviewers = await self._get_reviewers(subject_id=subject.id)
        students_data = await self._get_students_data(
            subject_id=subject.id,
            homeworks=homeworks,
        )
        distribution = Distribution(
            params=params,
            homeworks=homeworks,
            reviewers=reviewers,
        )
        await distribution.distribute(students_data=students_data)
        new_folder_id = await self._create_folder_for_homeworks(
            parent_folder_id=subject.drive_folder_id,
            homework_ids=params.homework_ids,
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

    async def _add_folder_to_notification(
        self, subject_id: int, folder_id: str
    ) -> None:
        subject = await self.uow.subject.read_by_id(subject_id=subject_id)
        folder_ids_key = "regular_notification_folder_ids_" + subject.eng_name
        folder_ids_str = await self.settings.get(folder_ids_key)
        folder_ids = get_cleaned_folder_ids(folder_ids_str)
        if len(folder_ids) >= 20:
            del folder_ids[0]
        folder_ids.append(folder_id)
        await self.settings.update(key=folder_ids_key, value="\n".join(folder_ids))

    async def _save_distribution(
        self,
        subject_id: int,
        distribution: Distribution,
    ) -> None:
        data = distribution.model_dump(mode="json")
        await self.uow.distribution.create(
            subject_id=subject_id,
            data=data,
        )

    @threaded
    def _create_folder_for_homeworks(
        self,
        parent_folder_id: str,
        homework_ids: Sequence[int],
    ) -> str:
        now = datetime.now()
        folder_title = NameGen(homework_ids=homework_ids, dt=now).folder_title
        new_folder = self.google_drive.make_new_folder(
            new_folder_title=folder_title,
            parent_folder_id=parent_folder_id,
        )
        self.google_drive.set_permissions_for_anyone(folder_id=new_folder.id)
        return new_folder.id

    @threaded
    def _write_data_in_new_sheet(
        self,
        spreadsheet_id: str,
        distribution: Distribution,
    ) -> None:
        now = datetime.now()
        sheet_title = NameGen(
            homework_ids=distribution.params.homework_ids,
            dt=now,
        ).sheet_title
        self.google_sheets.create_sheet(
            spreadsheet_id=spreadsheet_id,
            title=sheet_title,
            index=SHEET_INDEX,
        )
        self.google_sheets.set_data(
            spreadsheet_id=spreadsheet_id,
            range_sheet=sheet_title,
            values=distribution.serialize_for_sheet(),
            major_dimension=SHEET_MAJOR_DIMENSION,
        )
