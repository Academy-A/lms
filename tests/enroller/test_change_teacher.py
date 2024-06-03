from dirty_equals import IsPartialDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import TeacherAssignment
from lms.generals.enums import TeacherType
from lms.logic.enroll_student import Enroller


async def test_change_teacher_if_same_teacher(
    enroller: Enroller,
    session: AsyncSession,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
    create_teacher_assignment,
):
    product = await create_product()
    teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(
        product=product,
        teacher_type=TeacherType.CURATOR,
    )
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=teacher_product,
        teacher_type=TeacherType.CURATOR,
    )
    ta = await create_teacher_assignment(
        teacher_product=teacher_product,
        student_product=student_product,
        removed_at=None,
    )
    async with enroller.uow.start():
        await enroller.change_teacher_for_student(
            product_id=product.id,
            student_vk_id=student_product.student.vk_id,
            teacher_vk_id=teacher_product.teacher.vk_id,
        )
    await session.refresh(ta)
    assert ta.as_dict() == IsPartialDict(
        {
            "removed_at": None,
            "student_product_id": student_product.id,
            "teacher_product_id": teacher_product.id,
        }
    )


async def test_change_teacher_if_have_not_teacher_earlier(
    enroller: Enroller,
    session: AsyncSession,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
):
    product = await create_product()
    teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(
        product=product,
        teacher_type=TeacherType.CURATOR,
    )
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=None,
        teacher_type=None,
    )
    async with enroller.uow.start():
        await enroller.change_teacher_for_student(
            product_id=product.id,
            student_vk_id=student_product.student.vk_id,
            teacher_vk_id=teacher_product.teacher.vk_id,
        )
        await enroller.uow.commit()

    await session.refresh(student_product)
    assert student_product.as_dict() == IsPartialDict(
        {
            "teacher_product_id": teacher_product.id,
            "teacher_type": teacher_product.type,
        }
    )


async def test_change_teacher_if_old_teacher_product_ok_change_teacher(
    enroller: Enroller,
    session: AsyncSession,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
):
    product = await create_product()
    old_teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.MENTOR,
    )
    new_teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(product=product, teacher_type=None)
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=old_teacher_product,
        teacher_type=old_teacher_product.type,
    )
    async with enroller.uow.start():
        await enroller.change_teacher_for_student(
            product_id=product.id,
            student_vk_id=student_product.student.vk_id,
            teacher_vk_id=new_teacher_product.teacher.vk_id,
        )
        await enroller.uow.commit()

    await session.refresh(student_product)
    assert student_product.teacher_product_id == new_teacher_product.id


async def test_change_teacher_ifold_teacher_product_ok_teacher_assignment(
    enroller: Enroller,
    session: AsyncSession,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
):
    product = await create_product()
    old_teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.MENTOR,
    )
    new_teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(product=product, teacher_type=None)
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=old_teacher_product,
        teacher_type=old_teacher_product.type,
    )
    async with enroller.uow.start():
        await enroller.change_teacher_for_student(
            product_id=product.id,
            student_vk_id=student_product.student.vk_id,
            teacher_vk_id=new_teacher_product.teacher.vk_id,
        )
        await enroller.uow.commit()

    await session.refresh(student_product)
    ta = (
        await session.scalars(
            select(TeacherAssignment).filter_by(
                teacher_product_id=new_teacher_product.id,
                student_product_id=student_product.id,
            )
        )
    ).one()
    assert ta.as_dict() == IsPartialDict(
        {
            "teacher_product_id": new_teacher_product.id,
            "student_product_id": student_product.id,
            "removed_at": None,
        }
    )
