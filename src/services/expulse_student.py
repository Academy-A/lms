from datetime import datetime

from src.db.models import StudentProduct
from src.db.uow import UnitOfWork
from src.exceptions import StudentNotFoundError, StudentProductNotFoundError


async def expulse_student_by_offer_id(
    uow: UnitOfWork, student_vk_id: int, offer_id: int
) -> None:
    student = await uow.student.read_by_vk_id(vk_id=student_vk_id)
    if student is None:
        raise StudentNotFoundError
    offer = await uow.offer.read_by_id(offer_id=offer_id)
    student_product = await uow.student_product.find_by_student_and_product(
        student_id=student.id,
        product_id=offer.product_id,
    )
    if student_product is None:
        raise StudentProductNotFoundError
    now = datetime.now()
    await uow.student_product.update(
        StudentProduct.id == student_product.id,
        expulsion_at=now,
        teacher_type=None,
        teacher_product_id=None,
    )
    if student_product.teacher_product_id is not None:
        await uow.teacher_assignment.expulse_from_teacher_assignment(
            student_product_id=student_product.id,
            teacher_product_id=student_product.teacher_product_id,
        )
