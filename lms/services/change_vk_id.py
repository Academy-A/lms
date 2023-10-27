from lms.db.models import Student
from lms.db.uow import UnitOfWork
from lms.dto import StudentDto


async def change_student_vk_id_by_soho_id(
    uow: UnitOfWork, soho_id: int, vk_id: int
) -> StudentDto:
    soho = await uow.soho.read_by_id(soho_id=soho_id)
    return await uow.student.update(
        Student.id == soho.student_id,
        vk_id=vk_id,
    )
