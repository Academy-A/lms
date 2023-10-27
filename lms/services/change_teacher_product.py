from datetime import datetime

from fastapi import BackgroundTasks

from lms.clients.autopilot import send_teacher_to_autopilot
from lms.db.models import StudentProduct
from lms.db.uow import UnitOfWork
from lms.exceptions.student import StudentNotFoundError, StudentProductNotFoundError
from lms.exceptions.teacher import TeacherAssignmentNotFoundError


async def change_teacher_for_student(
    uow: UnitOfWork,
    background_tasks: BackgroundTasks,
    product_id: int,
    student_vk_id: int,
    teacher_vk_id: int,
) -> None:
    student = await uow.student.read_by_vk_id(vk_id=student_vk_id)
    if student is None:
        raise StudentNotFoundError
    teacher = await uow.teacher.read_by_vk_id(vk_id=teacher_vk_id)
    product = await uow.product.read_by_id(product_id=product_id)
    subject = await uow.subject.find_by_product(product_id=product.id)
    student_product = await uow.student_product.find_by_student_and_product(
        student_id=student.id,
        product_id=product.id,
    )
    if student_product is None:
        raise StudentProductNotFoundError

    teacher_product = await uow.teacher_product.find_by_teacher_and_product(
        teacher_id=teacher.id,
        product_id=product.id,
    )
    if (
        student_product.teacher_product_id is not None
        and student_product.teacher_product_id != teacher_product.id
    ):
        try:
            await uow.teacher_assignment.expulse_from_teacher_assignment(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
        except TeacherAssignmentNotFoundError:
            pass
    if student_product.teacher_product_id != teacher_product.id:
        await uow.student_product.update(
            StudentProduct.id == student_product.id,
            teacher_product_id=teacher_product.id,
            teacher_type=teacher_product.type,
        )
        await uow.teacher_assignment.create(
            student_product_id=student_product.id,
            teacher_product_id=teacher_product.id,
            assignment_at=datetime.now(),
        )
    background_tasks.add_task(
        send_teacher_to_autopilot,
        target_url=subject.autopilot_url,
        student_vk_id=student.vk_id,
        teacher_vk_id=teacher.vk_id,
        teacher_type=teacher_product.type,
    )
