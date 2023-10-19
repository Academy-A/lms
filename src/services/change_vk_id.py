from src.db.models import Student
from src.db.uow import UnitOfWork
from src.dto import StudentData


async def change_student_vk_id_by_soho_id(
    uow: UnitOfWork, soho_id: int, vk_id: int
) -> StudentData:
    soho = await uow.soho.read_by_id(soho_id=soho_id)
    return await uow.student.update(
        Student.id == soho.student_id,
        vk_id=vk_id,
    )
