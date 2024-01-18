from lms.db.uow import UnitOfWork
from lms.generals.models.student import Student


async def change_student_vk_id_by_soho_id(
    uow: UnitOfWork, soho_id: int, vk_id: int
) -> Student:
    soho = await uow.soho.read_by_id(soho_id=soho_id)
    return await uow.student.update_vk_id(
        student_id=soho.student_id,
        vk_id=vk_id,
    )
