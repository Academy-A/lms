from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from src.enums import TeacherType

if TYPE_CHECKING:
    from src.db.models import Flow, Soho, Student, StudentProduct


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
        )
