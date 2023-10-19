from datetime import datetime

from src.db.models import StudentProduct
from src.db.uow import UnitOfWork
from src.exceptions import StudentProductHasNotTeacherError, StudentProductNotFoundError


async def grade_teacher(
    uow: UnitOfWork, soho_id: int, product_id: int, grade: int
) -> None:
    soho = await uow.soho.read_by_id(soho_id=soho_id)
    await uow.product.read_by_id(product_id=product_id)
    student_product = await uow.student_product.find_by_student_and_product(
        student_id=soho.student_id,
        product_id=product_id,
    )
    if student_product is None:
        raise StudentProductNotFoundError
    if student_product.teacher_product_id is None:
        raise StudentProductHasNotTeacherError
    await uow.teacher_product.add_grade(
        teacher_product_id=student_product.teacher_product_id, grade=grade
    )
    await uow.student_product.update(
        StudentProduct.id == student_product.id,
        teacher_grade=grade,
        teacher_graded_at=datetime.now(),
    )
