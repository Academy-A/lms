from datetime import datetime

from lms.adapters.db.uow import UnitOfWork
from lms.exceptions import StudentProductHasNotTeacherError, StudentProductNotFoundError


async def grade_teacher(
    uow: UnitOfWork, soho_id: int, product_id: int, grade: int
) -> None:
    soho = await uow.soho.read_by_id(soho_id=soho_id)
    await uow.product.read_by_id(product_id=product_id)
    sp = await uow.student_product.find_by_student_and_product(
        student_id=soho.student_id,
        product_id=product_id,
    )
    if sp is None:
        raise StudentProductNotFoundError
    if sp.teacher_product_id is None:
        raise StudentProductHasNotTeacherError

    tp = await uow.teacher_product.read_by_id(
        teacher_product_id=sp.teacher_product_id,
    )
    new_counter = tp.grade_counter + 1
    new_average_grade = (tp.average_grade * tp.grade_counter + grade) / new_counter
    await uow.teacher_product.update_average_grade(
        teacher_product_id=tp.id,
        average_grade=new_average_grade,
        counter=new_counter,
    )
    await uow.student_product.update(
        student_product_id=sp.id,
        teacher_grade=grade,
        teacher_graded_at=datetime.now(),
    )
