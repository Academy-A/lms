from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, NamedTuple

from lms.enums import TeacherType

if TYPE_CHECKING:
    from lms.db.models import (
        Flow,
        Product,
        Reviewer,
        SohoAccount,
        Student,
        StudentProduct,
        Subject,
        Teacher,
        TeacherProduct,
        User,
        VerifiedWorkFile,
    )


@dataclass(slots=True)
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
class StudentDto:
    id: int
    vk_id: int
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, model: Student) -> StudentDto:
        return cls(
            id=model.id,
            vk_id=model.vk_id,
            first_name=model.first_name,
            last_name=model.last_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@dataclass
class SohoData:
    id: int
    email: str
    student_id: int

    @classmethod
    def from_orm(cls, model: SohoAccount) -> SohoData:
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
    created_at: datetime
    updated_at: datetime
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
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            subject_id=obj.subject_id,
            product_group_id=obj.product_group_id,
            check_spreadsheet_id=obj.check_spreadsheet_id,
            drive_folder_id=obj.drive_folder_id,
            start_date=obj.start_date,
            end_date=obj.end_date,
        )


@dataclass(frozen=True, slots=True)
class SubjectDto:
    id: int
    name: str
    eng_name: str
    autopilot_url: str
    group_vk_url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj: Subject) -> SubjectDto:
        return cls(
            id=obj.id,
            name=obj.name,
            eng_name=obj.eng_name,
            autopilot_url=obj.autopilot_url,
            group_vk_url=obj.group_vk_url,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


@dataclass(frozen=True, slots=True)
class TeacherDto:
    id: int
    created_at: datetime
    updated_at: datetime
    vk_id: int
    first_name: str
    last_name: str

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_orm(cls, obj: Teacher) -> TeacherDto:
        return cls(
            id=obj.id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            vk_id=obj.vk_id,
            first_name=obj.first_name,
            last_name=obj.last_name,
        )


@dataclass(frozen=True, slots=True)
class TeacherProductDto:
    id: int
    created_at: datetime
    updated_at: datetime
    teacher_id: int
    product_id: int
    type: TeacherType
    is_active: bool
    max_students: int
    average_grade: float
    grade_counter: int

    @property
    def is_mentor(self) -> bool:
        return self.type == TeacherType.MENTOR

    @property
    def is_curator(self) -> bool:
        return self.type == TeacherType.CURATOR

    @classmethod
    def from_orm(cls, obj: TeacherProduct) -> TeacherProductDto:
        return cls(
            id=obj.id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            teacher_id=obj.teacher_id,
            product_id=obj.product_id,
            type=obj.type,
            is_active=obj.is_active,
            max_students=obj.max_students,
            average_grade=obj.average_grade,
            grade_counter=obj.grade_counter,
        )


@dataclass(frozen=True, slots=True)
class HomeworkDto:
    student_name: str
    student_vk_id: int
    student_soho_id: int
    submission_url: str
    teacher_product_id: int | None


@dataclass(slots=True)
class ReviewerDto:
    id: int
    product_id: int
    first_name: str
    last_name: str
    email: str
    desired: int
    max_: int
    abs_max: int
    is_active: bool

    recheck: bool = False
    homeworks: list[HomeworkDto] = field(default_factory=list)
    actual: int = 0
    percent: float = 0.0

    @classmethod
    def from_orm(cls, obj: Reviewer) -> ReviewerDto:
        return cls(
            id=obj.id,
            first_name=obj.first_name,
            last_name=obj.last_name,
            product_id=obj.product_id,
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
        return self.abs_max > len(self.homeworks)

    @property
    def can_add_other(self) -> bool:
        return self.abs_max > len(self.homeworks)


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


@dataclass(frozen=True)
class VerifiedWorkFileData:
    id: int
    subject_id: int
    student_id: int | None
    file_id: str
    name: str
    url: str

    @classmethod
    def from_orm(cls, obj: VerifiedWorkFile) -> VerifiedWorkFileData:
        return VerifiedWorkFileData(
            id=obj.id,
            subject_id=obj.subject_id,
            student_id=obj.student_id,
            file_id=obj.file_id,
            name=obj.name,
            url=obj.url,
        )


class TeacherDashboardData(NamedTuple):
    teacher_product_id: int
    name: str
    vk_id: int
    is_active: bool
    type: TeacherType
    max_students_count: int
    filled_students_count: int
    average_grade: int
    flows: str


@dataclass(frozen=True)
class UserData:
    username: str
    password: str

    @classmethod
    def from_orm(cls, obj: User) -> UserData:
        return cls(
            username=obj.username,
            password=obj.password,
        )
