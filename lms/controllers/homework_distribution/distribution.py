import json
import logging
import random
from collections.abc import Sequence
from datetime import datetime, timedelta

from google_api_service_helper import GoogleDrive, GoogleKeys, GoogleSheets
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from lms.api.v1.product.schemas import DistributionTaskSchema
from lms.clients.soho.client import SohoClient
from lms.config import Settings
from lms.db.models import Product, Reviewer, Student, StudentProduct
from lms.dto import HomeworkDto, ProductDto, ReviewerDto
from lms.enums import TeacherType
from lms.exceptions.product import ProductNotFoundError
from lms.utils import get_setting

log = logging.getLogger(__name__)

GOOGLE_KEYS_SETTING = "google_keys"


def distribute_homeworks(
    settings: Settings,
    session: Session,
    distribution_task: DistributionTaskSchema,
) -> None:
    product = session.get(Product, distribution_task.product_id)
    if product is None:
        raise ProductNotFoundError

    product_dto = ProductDto.from_orm(product)

    homeworks = get_homeworks(
        session=session,
        soho_api_token=settings.SOHO_API_TOKEN,
        distribution_task=distribution_task,
    )
    reviewers = get_reviewers(session=session, product_id=product_dto.id)
    google_keys = GoogleKeys(**json.loads(get_setting(session, GOOGLE_KEYS_SETTING)))
    gs = GoogleSheets(google_keys=google_keys)
    gd = GoogleDrive(google_keys=google_keys)

    DistributionController(
        gs=gs,
        gd=gd,
        product=product_dto,
        distribution_task=distribution_task,
        reviewers=reviewers,
        homeworks=homeworks,
    ).create_distribution()


def get_reviewers(session: Session, product_id: int) -> list[ReviewerDto]:
    query = (
        select(Reviewer)
        .filter(Reviewer.product_id == product_id, Reviewer.is_active.is_(True))
        .order_by(Reviewer.id)
    )
    reviewers = session.scalars(query).all()
    return [ReviewerDto.from_orm(r) for r in reviewers]


def get_homeworks(
    session: Session,
    soho_api_token: str,
    distribution_task: DistributionTaskSchema,
) -> list[HomeworkDto]:
    homeworks: list[HomeworkDto] = []
    soho = SohoClient(auth_token=soho_api_token)
    for hw in distribution_task.homeworks:
        group_homeworks = soho.get_homeworks_for_reviews_sync(
            homework_id=hw.homework_id
        ).homeworks
        flow_filters = []
        if hw.filters:
            for f in hw.filters:
                flow_filters.append(
                    and_(
                        StudentProduct.teacher_type == f.teacher_type,
                        StudentProduct.flow_id == f.flow_id,
                    )
                )
        hw_filter = or_(False, *flow_filters)
        query = (
            select(Student.vk_id, Student.first_name, Student.last_name, StudentProduct)
            .join(Student, Student.id == StudentProduct.student_id)
            .where(
                StudentProduct.product_id == distribution_task.product_id,
                StudentProduct.expulsion_at.is_(None),
                Student.vk_id.in_([hw.vk_id for hw in group_homeworks]),
                hw_filter,
            )
        )
        for vk_id, first_name, last_name, student_product in session.execute(
            query
        ).all():
            for gh in group_homeworks:
                if gh.vk_id == vk_id:
                    teacher_product_id = (
                        student_product.teacher_product_id
                        if student_product.teacher_type == TeacherType.MENTOR
                        else None
                    )
                    homeworks.append(
                        HomeworkDto(
                            student_name=first_name + " " + last_name,
                            vk_student_id=vk_id,
                            soho_student_id=gh.client_id,
                            submission_url=str(gh.chat_url),
                            teacher_product_id=teacher_product_id,
                        )
                    )
    return list(set(homeworks))


class DistributionController:
    """Распределение."""

    INDEX_SHEET = 4

    def __init__(
        self,
        product: ProductDto,
        distribution_task: DistributionTaskSchema,
        reviewers: Sequence[ReviewerDto],
        homeworks: Sequence[HomeworkDto],
        gs: GoogleSheets,
        gd: GoogleDrive,
    ) -> None:
        self.product = product
        self.distribution_task = distribution_task
        self.reviewers = reviewers
        self.gs = gs
        self.gd = gd
        self.total_max = sum(r.optimal_max for r in reviewers)
        self.total_desired = sum(r.optimal_desired for r in reviewers)
        self.premium_homeworks = [
            h for h in homeworks if h.teacher_product_id is not None
        ]
        self.other_homeworks = [h for h in homeworks if h.teacher_product_id is None]
        self.extras: list[HomeworkDto] = []

    def create_distribution(self) -> None:
        self._distribute_premium_homeworks()
        self._distribute_other_homeworks()
        self._create_folder_for_essays()
        self._write_data_in_new_sheet()

    def _distribute_premium_homeworks(self) -> None:
        for hw in self.premium_homeworks:
            for reviewer in self.reviewers:
                if reviewer.teacher_product_id == hw.teacher_product_id and (
                    reviewer.can_add_prem
                ):
                    reviewer.premium.append(hw)
                    break
            else:
                self.other_homeworks.append(hw)

    def _distribute_other_homeworks(self) -> None:
        other_students_length = len(self.other_homeworks)
        self._calculate_percents()
        if (
            other_students_length < self.total_desired
            or other_students_length < self.total_max
        ):
            self._distribute_less_than()
        elif other_students_length == self.total_desired:
            self._distribute_desired()
        else:
            self._distribute_max()

        self._distribute_other_by_reviewer()
        total_actual = sum(r.actual for r in self.reviewers)
        self.extras.extend(self.other_homeworks[total_actual:])
        log.info("End of distribution other homeworks")

    def _calculate_percents(self) -> None:
        if len(self.other_homeworks) <= self.total_desired:
            for r in self.reviewers:
                r.percent = r.optimal_desired / self.total_desired
        else:
            for r in self.reviewers:
                r.percent = r.optimal_max / self.total_max

    def _write_data_in_new_sheet(self) -> None:
        counter = 0
        data: list[list[str | int]] = [
            [
                self.distribution_task.name,
                "",
                f"НАЗВАНИЕ ФАЙЛА: 1234567_Имя_Фамилия_{self.distribution_task.name}",
                "",
                "Проверенные в ЧАТ с РЕБЕНКОМ + В ПАПКУ:",
                f"https://drive.google.com/drive/folders/{self.new_folder_id}?usp=drive_link",
                "",
                "",
                "",
                "",
                "ДЕДЛАЙН В СУББОТУ, 23:59",
            ],
            [],
        ]
        for r in self.reviewers:
            counter += 1
            column_identify: list[str | int] = [
                r.first_name + " " + r.last_name,
                "Максимум (без премиумных)",
                "Премиумные:",
                "Остальные:",
                "Всего",
                "VK ID",
            ]
            column_name: list[int | str] = [
                r.id,
                r.optimal_max,
                len(r.premium),
                len(r.other),
                f"=COUNTA(OFFSET(A2;5;{3 + (5 * (counter - 1))};200;1))",
                "Имя Фамилия",
            ]
            for student in r.premium + r.other:
                column_identify.append(str(student.vk_student_id))
                column_name.append(
                    f'=HYPERLINK("{student.submission_url}";"{student.student_name}")'
                )
            data.extend([column_identify, column_name, [], [], []])
        extras_identify: list[int | str] = ["Переполнение максимума"]
        extras_name: list[str | int] = [""]
        for extra_student in self.extras:
            extras_identify.append(student.soho_student_id)
            extras_name.append(
                f'=HYPERLINK("{extra_student.submission_url}";"{student.student_name}")'
            )
        data.extend([[], extras_identify, extras_name, []])
        hw = "_".join(str(hw.homework_id) for hw in self.distribution_task.homeworks)
        new_title = f"{week_title()} ({hw}) " + datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )
        self.gs.create_sheet(
            spreadsheet_id=self.product.check_spreadsheet_id,
            title=new_title,
            index=self.INDEX_SHEET,
        )
        self.gs.set_data(
            spreadsheet_id=self.product.check_spreadsheet_id,
            range_sheet=new_title,
            values=data,
            major_dimension="COLUMNS",
        )

    def _create_folder_for_essays(self) -> None:
        [r.email for r in self.reviewers]
        hw = "_".join(str(hw.homework_id) for hw in self.distribution_task.homeworks)
        title = f"{self.product.name}_({hw})_Проверенные"
        new_folder = self.gd.make_new_folder(
            new_folder_title=title,
            parent_folder_id=self.product.drive_folder_id,
        )
        # self.gd.set_permissions_for_users_by_list(
        #     folder_id=new_folder_id,
        #     user_email_list=emails,
        # )
        self.gd.set_permissions_for_anyone(folder_id=new_folder.id)
        self.new_folder_id = new_folder.id
        return

    def _distribute_less_than(self) -> None:
        log.info("Start calculate actual per reviewer")
        actual = 0
        for r in self.reviewers:
            r.actual = int(r.percent * len(self.other_homeworks))
            actual += r.actual
        r_ind = 0
        for _ in range(len(self.other_homeworks) - actual):
            while True:
                if self.reviewers[r_ind].actual < self.reviewers[r_ind].optimal_desired:
                    self.reviewers[r_ind].actual += 1
                    break
                r_ind += 1
                r_ind %= len(self.reviewers)
        log.info("End calculate acutal per reviewer")

    def _distribute_desired(self) -> None:
        for r in self.reviewers:
            r.actual = r.optimal_desired

    def _distribute_max(self) -> None:
        for r in self.reviewers:
            r.actual = r.optimal_max

    def _distribute_other_by_reviewer(self) -> None:
        total_actual = sum(r.actual for r in self.reviewers)
        hws = self.other_homeworks[:total_actual]
        random.shuffle(hws)
        count = 5
        while len(hws) and count > 0:
            k = 0
            while k < len(hws):
                hw = hws.pop()
                for r in self.reviewers:
                    if r.actual != len(r.other):
                        r.other.append(hw)
                        hw = None  # type: ignore[assignment]
                        break
                if hw is not None:
                    hws.insert(0, hw)
                    k += 1
            count -= 1
        for hw in hws:
            for r in self.reviewers:
                if r.actual < len(r.other):
                    r.other.append(hw)


def week_title() -> str:
    """Получение диапазона недели"""
    today = datetime.today()
    begin_date = today - timedelta(days=today.weekday())
    end_date = today + timedelta(days=6 - today.isoweekday())
    return f"{begin_date.strftime('%d.%m')}-{end_date.strftime('%d.%m')}"
