from typing import NamedTuple

from lms.generals.enums import TeacherType


class TeacherDashboardRow(NamedTuple):
    teacher_product_id: int
    name: str
    vk_id: int
    is_active: bool
    type: TeacherType
    max_students_count: int
    filled_students_count: int
    average_grade: int
    grade_counter: int
    flows: str
