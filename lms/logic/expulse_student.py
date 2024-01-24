from datetime import datetime

from lms.db.uow import UnitOfWork
from lms.exceptions import (
    StudentNotFoundError,
    StudentProductAlreadyExpulsedError,
    StudentProductNotFoundError,
)


async def expulse_student_by_offer_id(
    uow: UnitOfWork, student_vk_id: int, product_id: int
) -> None:
    student = await uow.student.read_by_vk_id(vk_id=student_vk_id)
    if student is None:
        raise StudentNotFoundError
    await uow.product.read_by_id(product_id=product_id)
    student_product = await uow.student_product.find_by_student_and_product(
        student_id=student.id,
        product_id=product_id,
    )
    if student_product is None:
        raise StudentProductNotFoundError
    if student_product.expulsion_at is not None:
        raise StudentProductAlreadyExpulsedError
    now = datetime.now()
    await uow.student_product.update(
        student_product_id=student_product.id,
        expulsion_at=now,
        teacher_type=None,
        teacher_product_id=None,
    )
    if student_product.teacher_product_id is None:
        return
    teacher_product_id = await uow.teacher_assignment.find_last_teacher_product_id(
        student_product_id=student_product.id
    )
    if teacher_product_id is not None:
        await uow.teacher_assignment.expulse_student_safety(
            student_product_id=student_product.id,
            teacher_product_id=teacher_product_id,
        )
        return
    if teacher_product_id != student_product.teacher_product_id:
        await uow.teacher_assignment.create(
            student_product_id=student_product.id,
            teacher_product_id=student_product.teacher_product_id,
            removed_at=now,
            assignment_at=student_product.created_at,
        )
