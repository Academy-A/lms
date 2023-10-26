from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import field
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from pydantic.dataclasses import dataclass

from lms.enums import TeacherType

if TYPE_CHECKING:
    from lms.db.models import Flow, Product, Reviewer, Soho, Student, StudentProduct


@dataclass(frozen=True, slots=True)
class SubGroupDto:
    teacher_type: TeacherType | None
    flow_id: int | None


@dataclass(frozen=True, slots=True)
class HomeworkGroupDto:
    homework_id: int
    subgroups: Sequence[SubGroupDto]


@dataclass(frozen=True, slots=True)
class DistributionTaskDto:
    product_id: int
    name: str
    groups: Sequence[HomeworkGroupDto]


@dataclass
class PaginationData:
    items: Sequence[Any]
    page: int
    page_size: int
    total: int
    pages: int = field(init=False)

    def __post_init__(self) -> None:
        self.pages = int(math.ceil(self.total / self.page_size)) or 1


@dataclass
class NewStudentData:
    vk_id: int
    soho_id: int
    email: str
    first_name: str | None
    last_name: str | None
    flow_id: int


@dataclass
class StudentData:
    id: int
    vk_id: int
    first_name: str
    last_name: str

    @classmethod
    def from_orm(cls, model: Student) -> StudentData:
        return StudentData(
            id=model.id,
            vk_id=model.vk_id,
            first_name=model.first_name,
            last_name=model.last_name,
        )


@dataclass
class SohoData:
    id: int
    email: str
    student_id: int

    @classmethod
    def from_orm(cls, model: Soho) -> SohoData:
        return SohoData(
            id=model.id,
            email=model.email,
            student_id=model.student_id,
        )


@dataclass
class FlowData:
    id: int

    @classmethod
    def from_orm(cls, model: Flow) -> FlowData:
        return FlowData(id=model.id)


@dataclass
class StudentProductData:
    id: int
    student_id: int
    product_id: int
    teacher_product_id: int | None
    teacher_type: TeacherType | None
    offer_id: int
    flow_id: int | None
    cohort: int
    teacher_grade: int | None
    teacher_graded_at: datetime | None
    expulsion_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        return self.expulsion_at is None

    @property
    def is_alone(self) -> bool:
        return self.teacher_type is None

    @classmethod
    def from_orm(cls, model: StudentProduct) -> StudentProductData:
        return StudentProductData(
            id=model.id,
            student_id=model.student_id,
            product_id=model.product_id,
            teacher_product_id=model.teacher_product_id,
            teacher_type=model.teacher_type,
            offer_id=model.offer_id,
            flow_id=model.flow_id,
            cohort=model.cohort,
            teacher_grade=model.teacher_grade,
            teacher_graded_at=model.teacher_graded_at,
            expulsion_at=model.expulsion_at,
            created_at=model.created_at,
            updated_at=model.created_at,
        )


@dataclass(frozen=True, slots=True)
class ProductDto:
    id: int
    name: str
    subject_id: int
    product_group_id: int
    check_spreadsheet_id: str
    drive_folder_id: str
    start_date: date | None
    end_date: date | None

    @classmethod
    def from_orm(cls, obj: Product) -> ProductDto:
        return cls(
            id=obj.id,
            name=obj.name,
            subject_id=obj.subject_id,
            product_group_id=obj.product_group_id,
            check_spreadsheet_id=obj.check_spreadsheet_id,
            drive_folder_id=obj.drive_folder_id,
            start_date=obj.start_date,
            end_date=obj.end_date,
        )


@dataclass(frozen=True, slots=True)
class HomeworkDto:
    student_name: str
    vk_student_id: int
    soho_student_id: int
    submission_url: str
    teacher_product_id: int | None


@dataclass(slots=True)
class ReviewerDto:
    id: int
    product_id: int
    first_name: str
    last_name: str
    teacher_product_id: int | None
    email: str
    desired: int
    max_: int
    abs_max: int
    is_active: bool

    recheck: bool = False
    premium: list[HomeworkDto] = field(default_factory=list)
    other: list[HomeworkDto] = field(default_factory=list)
    actual: int = 0
    percent: float = 0.0

    @classmethod
    def from_orm(cls, obj: Reviewer) -> ReviewerDto:
        return cls(
            id=obj.id,
            first_name=obj.first_name,
            last_name=obj.last_name,
            product_id=obj.product_id,
            teacher_product_id=obj.teacher_product_id,
            email=obj.email,
            desired=obj.desired,
            max_=obj.max_,
            abs_max=obj.abs_max,
            is_active=obj.is_active,
        )

    @property
    def optimal_desired(self) -> int:
        return min(self.desired, self.abs_max)

    @property
    def optimal_max(self) -> int:
        return min(self.max_, self.abs_max)

    @property
    def can_add_prem(self) -> bool:
        return self.abs_max > len(self.premium)

    @property
    def can_add_other(self) -> bool:
        return self.abs_max > len(self.premium) + len(self.other)
