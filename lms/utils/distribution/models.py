import random
from collections.abc import MutableSequence, Sequence
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from lms.clients.soho import SohoHomework
from lms.db.repositories.student_product import StudentDistributeData
from lms.generals.enums import DistributionErrorMessage
from lms.generals.models.distribution import DistributionParams
from lms.generals.models.reviewer import Reviewer


class ErrorHomework(BaseModel):
    homework: SohoHomework
    error_message: DistributionErrorMessage


class StudentHomework(BaseModel):
    student_name: str
    student_vk_id: int
    student_soho_id: int
    submission_url: HttpUrl
    teacher_product_id: int | None = None


class DistributionReviewer(Reviewer):
    recheck: bool = False
    student_homeworks: list[StudentHomework] = Field(default_factory=list)
    actual: int = 0
    percent: float = 0.0

    @property
    def optimal_desired(self) -> int:
        return min(self.desired, self.abs_max)

    @property
    def optimal_max(self) -> int:
        return min(self.max_, self.abs_max)


class Distribution(BaseModel):
    params: DistributionParams
    homeworks: Sequence[SohoHomework]
    reviewers: Sequence[DistributionReviewer]

    error_homeworks: list[ErrorHomework] = Field(default_factory=list)
    new_folder_id: str | None = None

    async def distribute(self, students_data: Sequence[StudentDistributeData]) -> None:
        pre_filtered_homeworks = await self._match_homeworks_and_students(students_data)
        random.shuffle(pre_filtered_homeworks)
        await self._distribute_minimum(homeworks=pre_filtered_homeworks)
        await self._distribute_premium(homeworks=pre_filtered_homeworks)
        await self._distribute_main(homeworks=pre_filtered_homeworks)
        await self._distribute_rechecks()

    async def _match_homeworks_and_students(
        self,
        student_datas: Sequence[StudentDistributeData],
    ) -> MutableSequence[StudentHomework]:
        pre_filtered_homeworks: list[StudentHomework] = list()
        student_data: dict[int, StudentDistributeData] = {
            st.vk_id: st for st in student_datas
        }
        for hw in self.homeworks:
            if hw.student_vk_id is None:
                self.error_homeworks.append(
                    ErrorHomework(
                        homework=hw,
                        error_message=DistributionErrorMessage.HOMEWORK_WITHOUT_VK_ID,
                    )
                )
            elif hw.student_vk_id not in student_data:
                self.error_homeworks.append(
                    ErrorHomework(
                        homework=hw,
                        error_message=DistributionErrorMessage.STUDENT_WITH_VK_ID_NOT_FOUND,
                    )
                )
            elif student_data[hw.student_vk_id].is_expulsed:
                self.error_homeworks.append(
                    ErrorHomework(
                        homework=hw,
                        error_message=DistributionErrorMessage.STUDENT_WAS_EXPULSED,
                    )
                )
            else:
                pre_filtered_homeworks.append(
                    StudentHomework(
                        student_name=student_data[hw.student_vk_id].name,
                        student_vk_id=student_data[hw.student_vk_id].vk_id,
                        student_soho_id=hw.student_soho_id,
                        submission_url=hw.chat_url,
                        teacher_product_id=student_data[
                            hw.student_vk_id
                        ].teacher_product_id,
                    )
                )
        return pre_filtered_homeworks

    async def _distribute_minimum(
        self, homeworks: MutableSequence[StudentHomework]
    ) -> None:
        for r in self.reviewers:
            for _ in range(r.min_ - len(r.student_homeworks)):
                if homeworks:
                    r.student_homeworks.append(homeworks.pop())

    async def _distribute_premium(
        self, homeworks: MutableSequence[StudentHomework]
    ) -> None:
        pass

    async def _distribute_main(
        self, homeworks: MutableSequence[StudentHomework]
    ) -> None:
        self._calculate_actual(homeworks_count=len(homeworks))
        self._filled_main(homeworks=homeworks)

    async def _distribute_rechecks(self) -> None:
        pass

    def _calculate_actual(self, homeworks_count: int) -> None:  # noqa: C901
        total_desired = sum(r.optimal_desired for r in self.reviewers)
        total_max = sum(r.optimal_max for r in self.reviewers)
        if homeworks_count <= total_desired:
            for r in self.reviewers:
                r.percent = r.optimal_desired / total_desired
        else:
            for r in self.reviewers:
                r.percent = r.optimal_max / total_max

        if homeworks_count < total_desired or homeworks_count < total_max:
            actual = 0
            for r in self.reviewers:
                r.actual = int(r.percent * homeworks_count)
                actual += r.actual
            r_ind = 0
            for _ in range(homeworks_count - actual):
                while True:
                    if (
                        self.reviewers[r_ind].actual
                        < self.reviewers[r_ind].optimal_desired
                    ):
                        self.reviewers[r_ind].actual += 1
                        break
                    r_ind += 1
                    r_ind %= len(self.reviewers)
        elif homeworks_count == total_desired:
            for r in self.reviewers:
                r.actual = r.optimal_desired
        else:
            for r in self.reviewers:
                r.actual = r.optimal_max

    def _filled_main(self, homeworks: MutableSequence[StudentHomework]) -> None:
        total_actual = sum(r.actual for r in self.reviewers)
        hws = homeworks[:total_actual]
        count = 5
        while len(hws) and count > 0:
            k = 0
            while k < len(hws):
                hw = hws.pop()
                for r in self.reviewers:
                    if r.actual != len(r.student_homeworks):
                        r.student_homeworks.append(hw)
                        hw = None  # type: ignore[assignment]
                        break
                if hw is not None:
                    hws.insert(0, hw)
                    k += 1
            count -= 1
        for hw in hws:
            for r in self.reviewers:
                if r.actual < len(r.student_homeworks):
                    r.student_homeworks.append(hw)
        for hw in homeworks[total_actual:]:
            self.error_homeworks.append(
                ErrorHomework(
                    homework=SohoHomework(
                        clientHomeworkId=0,
                        clientId=0,
                        sentToReviewAt=datetime.now(),
                        chatUrl=hw.submission_url,
                        vk_id=hw.student_vk_id,
                    ),
                    error_message=DistributionErrorMessage.STACK_OVERFLOW,
                )
            )

    def serialize_for_sheet(self) -> Sequence[Sequence[Any]]:
        data: list[list[str | int]] = [
            [
                self.params.name,
                "",
                f"НАЗВАНИЕ ФАЙЛА: 1234567_Имя_Фамилия_{self.params.name}",
                "",
                "Проверенные в ЧАТ с РЕБЕНКОМ + В ПАПКУ:",
                f"https://drive.google.com/drive/folders/{self.new_folder_id}",
                "",
                "",
                "",
                "",
                "ДЕДЛАЙН В СУББОТУ, 23:59",
            ],
            [],
        ]
        counter = 0
        for r in self.reviewers:
            counter += 1
            column_identify: list[str | int] = [
                r.first_name + " " + r.last_name,
                "Максимум ",
                "Факт:",
                "Всего",
                "VK ID",
            ]
            column_name: list[int | str] = [
                r.id,
                r.optimal_max,
                len(r.student_homeworks),
                f"=COUNTA(OFFSET(A2;5;{3 + (5 * (counter - 1))};200;1))",
                "Имя Фамилия",
            ]
            for hw in r.student_homeworks:
                column_identify.append(str(hw.student_vk_id))
                column_name.append(
                    f'=HYPERLINK("{hw.submission_url}";"{hw.student_name}")'
                )
            data.extend([column_identify, column_name, [], [], []])
        error_identify: list[int | str] = ["Домашние работы с ошибками"]
        error_name: list[str | int] = [""]
        error_message: list[str | int] = [""]
        for e_hw in self.error_homeworks:
            error_identify.append(e_hw.homework.student_soho_id)
            error_name.append(
                f'=HYPERLINK("{e_hw.homework.chat_url}";"Ссылка на работу")'
            )
            error_message.append(e_hw.error_message)
        data.extend([[], error_identify, error_name, error_message])
        return data
