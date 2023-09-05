from src.exceptions.base import EntityNotFoundError


class TeacherNotFoundError(EntityNotFoundError):
    pass


class TeacherProductNotFoundError(EntityNotFoundError):
    pass


class TeacherAssignmentNotFoundError(EntityNotFoundError):
    pass
