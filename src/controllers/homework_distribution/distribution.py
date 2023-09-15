from datetime import datetime, timedelta
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from google_api_service_helper import GoogleDrive, GoogleSpreadsheet

from src.clients.soho.client import SohoClient
from src.config import Settings
from src.controllers.homework_distribution.dto import (
    ReviewerDTO,
    HomeworkDTO,
    ProductDTO,
)
from src.db.models import (
    Product,
    Reviewer,
    Setting,
    Student,
    StudentProduct,
)
from src.enums import TeacherType
from src.exceptions.product import ProductNotFoundError

GOOGLE_KEYS_SETTING = "google_keys"


def distribute_homeworks(
    settings: Settings,
    session: Session,
    homework_id: int,
    product_id: int,
    teacher_types: list[str | None],
) -> None:
    product = session.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError

    product_dto = ProductDTO(
        name=product.name,
        drive_folder_id=product.drive_folder_id,
        check_spreadsheet_id=product.check_spreadsheet_id,
    )

    homeworks = get_homeworks(
        session=session,
        homework_id=homework_id,
        product_id=product_id,
        soho_api_token=settings.SOHO_API_TOKEN,
        teacher_types=teacher_types,
    )
    reviewers = get_reviewers(session=session, product_id=product_id)
    google_keys = json.loads(get_setting_by_key(session, GOOGLE_KEYS_SETTING))
    gs = GoogleSpreadsheet(google_keys=google_keys)
    gd = GoogleDrive(google_keys=google_keys)

    DistributionController(
        gs=gs,
        gd=gd,
        product=product_dto,
        homework_id=homework_id,
        reviewers=reviewers,
        homeworks=homeworks,
    ).create_distribution()


def get_setting_by_key(session: Session, key: str) -> str:
    query = select(Setting).filter_by(key=key)
    return session.scalars(query).one().value


def get_reviewers(session: Session, product_id: int) -> list[ReviewerDTO]:
    query = select(Reviewer).filter(
        Reviewer.product_id == product_id, Reviewer.is_active.is_(True)
    )
    reviewers = session.scalars(query).all()
    return [
        ReviewerDTO(
            id=r.id,
            name=r.fullname,
            product_id=r.product_id,
            teacher_product_id=r.teacher_product_id,
            email=r.email,
            desired=r.desired,
            max_=r.max_,
            abs_max=r.abs_max,
        )
        for r in reviewers
    ]


def get_homeworks(
    session: Session,
    homework_id: int,
    product_id: int,
    soho_api_token: str,
    teacher_types: list[str | None],
) -> list[HomeworkDTO]:
    soho = SohoClient(auth_token=soho_api_token)
    homeworks = soho.get_homeworks_for_reviews_sync(homework_id=homework_id).homeworks

    query = (
        select(Student.vk_id, Student.fullname, StudentProduct)
        .join(Student, Student.id == StudentProduct.student_id)
        .where(
            StudentProduct.product_id == product_id,
            StudentProduct.expulsion_at.is_(None),
            StudentProduct.teacher_type.in_(teacher_types),
            Student.vk_id.in_([hw.vk_id for hw in homeworks]),
        )
    )
    hws = []
    for vk_id, fullname, student_product in session.execute(query).all():
        for homework in homeworks:
            if homework.vk_id == vk_id:
                mentor_id = (
                    student_product.teacher_product_id
                    if student_product.teacher_type == TeacherType.MENTOR
                    else None
                )
                hws.append(
                    HomeworkDTO(
                        student_name=fullname,
                        vk_student_id=vk_id,
                        soho_student_id=homework.client_id,
                        submission_url=str(homework.chat_url),
                        mentor_id=mentor_id,
                    )
                )
    return hws


class DistributionController:
    """Распределение."""

    def __init__(
        self,
        product: ProductDTO,
        homework_id: int,
        reviewers: list[ReviewerDTO],
        homeworks: list[HomeworkDTO],
        gs: GoogleSpreadsheet,
        gd: GoogleDrive,
    ) -> None:
        self.product = product
        self.homework_id = homework_id
        self.reviewers = reviewers
        self.gs = gs
        self.gd = gd
        self.max = sum(r.optimal_max for r in reviewers)
        self.total_desired = sum(r.optimal_desired for r in reviewers)
        self.premium_homeworks = [h for h in homeworks if h.mentor_id is not None]
        self.other_homeworks = [h for h in homeworks if h.mentor_id is None]
        self.extras: list[HomeworkDTO] = []

    def create_distribution(self) -> None:
        self._distribute_premium_homeworks()
        self._distribute_other_homeworks()

        self._write_data_in_new_sheet()
        self._create_folder_for_essays()

    def _distribute_premium_homeworks(self) -> None:
        return

    def _distribute_other_homeworks(self) -> None:
        return

    def _write_data_in_new_sheet(self) -> None:
        counter = 0
        data: list[list[str | int]] = [[], []]
        for r in self.reviewers:
            counter += 1
            column_identify: list[str | int] = [
                r.name,
                "Максимум (без премиумных)",
                "Премиумные:",
                "Остальные:",
                "Всего",
                "SOHO ID",
            ]
            column_name: list[int | str] = [
                r.id,
                r.max_,
                len(r.premium),
                len(r.other),
                f"=COUNTA(OFFSET(A2;5;{3 + (5 * (counter - 1))};200;1))",
                "Имя Фамилия",
            ]
            for student in r.premium + r.other:
                column_identify.append(str(student.soho_student_id))
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

        new_title = f"{week_title()} ({self.homework_id}) " + datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )
        self.gs.create_sheet(
            ss_id=self.product.check_spreadsheet_id, title=new_title, index=3
        )
        self.gs.set_data(
            ss_id=self.product.check_spreadsheet_id, range_sheet=new_title, values=data
        )

    def _create_folder_for_essays(self) -> None:
        emails = [r.email for r in self.reviewers]
        title = f"{self.product.name}_{self.homework_id}_Проверенные"
        new_folder_id = self.gd.make_new_folder(
            new_folder_title=title,
            parent_folder_id=self.product.drive_folder_id,
            parent_folder_name="random",
        )
        self.gd.set_permissions_for_users_by_list(
            folder_id=new_folder_id,
            user_email_list=emails,
        )
        self.gd.set_permissions_for_anyone(folder_id=new_folder_id)
        return


def week_title() -> str:
    """Получение диапазона недели"""
    today = datetime.today()
    begin_date = today - timedelta(days=today.weekday())
    end_date = today + timedelta(days=6 - today.isoweekday())
    return f"{begin_date.strftime('%d.%m')}-{end_date.strftime('%d.%m')}"
