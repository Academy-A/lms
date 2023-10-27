from lms.exceptions.base import EntityNotFoundError


class TeacherNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "Teacher not found"
        super().__init__(detail, *args)


class TeacherProductNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "TeacherProduct not found"
        super().__init__(detail, *args)


class TeacherAssignmentNotFoundError(EntityNotFoundError):
    def __init__(self, *args: object) -> None:
        detail = "TeacherAssignment not found"
        super().__init__(detail, *args)
