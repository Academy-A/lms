from dataclasses import dataclass, field


@dataclass
class HomeworkDTO:
    student_name: str
    vk_student_id: int
    soho_student_id: int
    submission_url: str
    mentor_id: int | None = None


@dataclass
class ReviewerDTO:
    id: int
    product_id: int
    name: str
    teacher_product_id: int | None
    email: str
    desired: int
    max_: int
    abs_max: int
    recheck: bool = False
    premium: list[HomeworkDTO] = field(default_factory=list)
    other: list[HomeworkDTO] = field(default_factory=list)
    actual: int = 0
    percent: float = 0.0

    @property
    def optimal_desired(self) -> int:
        return min(self.desired, self.abs_max)

    @property
    def optimal_max(self) -> int:
        return min(self.max_, self.abs_max)


@dataclass
class ProductDTO:
    name: str
    drive_folder_id: str
    check_spreadsheet_id: str
