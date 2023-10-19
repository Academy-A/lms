from collections.abc import Sequence
from dataclasses import asdict

from fastapi import BackgroundTasks
from loguru import logger as log

from src.clients.autopilot import send_teacher_to_autopilot
from src.db.models import Offer, StudentProduct
from src.db.uow import UnitOfWork
from src.dto import NewStudentData, StudentProductData


async def enroll_student(
    uow: UnitOfWork,
    background_tasks: BackgroundTasks,
    new_student: NewStudentData,
    offer_ids: Sequence[int],
) -> StudentProductData:
    log.info("Enroll student with data {data}", data=asdict(new_student))
    student = await uow.student.read_by_vk_id(vk_id=new_student.vk_id)
    if student is None:
        student = await uow.student.create(
            first_name=new_student.first_name,
            last_name=new_student.last_name,
            vk_id=new_student.vk_id,
        )
        await uow.soho.create(
            soho_id=new_student.soho_id,
            student_id=student.id,
            email=new_student.email,
        )
    offer_id = offer_ids[0]
    offer = await uow.offer.read_by_id(offer_id=offer_id)
    old_student_product = await uow.student_product.find_by_student_and_product(
        student_id=student.id,
        product_id=offer.product_id,
    )
    if old_student_product is not None:
        return await enroll_student_again_by_offer(
            uow=uow,
            background_tasks=background_tasks,
            student_product=old_student_product,
            new_offer=offer,
        )
    flow = await uow.flow.get_by_soho_id(new_student.flow_id)
    student_product = await enroll_student_by_offer_id(
        uow=uow,
        student_id=student.id,
        offer_id=offer_id,
        flow_id=flow.id if flow else None,
    )
    if student_product.teacher_product_id and student_product.teacher_type:
        subject = await uow.product.find_subject_by_product(
            product_id=student_product.product_id,
        )
        teacher = await uow.teacher.find_teacher_by_teacher_product(
            teacher_product_id=student_product.teacher_product_id,
        )
        background_tasks.add_task(
            send_teacher_to_autopilot,
            target_url=subject.autopilot_url,
            student_vk_id=student.vk_id,
            teacher_vk_id=teacher.vk_id,
            teacher_type=student_product.teacher_type,
        )
    return student_product


async def enroll_student_by_offer_id(
    uow: UnitOfWork,
    student_id: int,
    offer_id: int,
    flow_id: int | None = None,
) -> StudentProductData:
    offer = await uow.offer.read_by_id(offer_id=offer_id)
    teacher_product = None
    if offer.teacher_type is not None:
        teacher_product = await uow.teacher_product.get_for_enroll(
            product_id=offer.product_id,
            teacher_type=offer.teacher_type,
            flow_id=flow_id,
        )
    student_product = await uow.student_product.create(
        student_id=student_id,
        product_id=offer.product_id,
        cohort=offer.cohort,
        offer_id=offer.id,
        teacher_type=offer.teacher_type,
        teacher_product_id=teacher_product.id if teacher_product else None,
        flow_id=flow_id,
    )
    if teacher_product is not None:
        await uow.teacher_assignment.create(
            student_product_id=student_product.id,
            teacher_product_id=teacher_product.id,
        )
    return student_product


async def enroll_student_again_by_offer(
    uow: UnitOfWork,
    background_tasks: BackgroundTasks,
    student_product: StudentProductData,
    new_offer: Offer,
) -> StudentProductData:
    old_offer = await uow.offer.read_by_id(student_product.offer_id)
    if (
        (not student_product.is_active or student_product.is_alone)
        and new_offer.is_alone
        or (
            student_product.is_active
            and new_offer.teacher_type == old_offer.teacher_type
        )
    ):
        pass
    elif (
        student_product.is_active
        and not student_product.is_alone
        and new_offer.is_alone
    ):
        await uow.teacher_assignment.expulse_from_teacher_assignment(
            student_product_id=student_product.id,
            teacher_product_id=student_product.teacher_product_id,  # type: ignore[arg-type]
        )
        student_product.teacher_product_id = None
        student_product.teacher_type = None
    elif not new_offer.is_alone:
        if not old_offer.is_alone:
            await uow.teacher_assignment.expulse_from_teacher_assignment(
                student_product_id=student_product.id,
                teacher_product_id=student_product.teacher_product_id,  # type: ignore[arg-type]
            )
        teacher_product = await uow.teacher_product.get_for_enroll(
            product_id=new_offer.product_id,
            teacher_type=new_offer.teacher_type,  # type: ignore[arg-type]
            flow_id=student_product.flow_id,
        )
        student_product.teacher_type = new_offer.teacher_type
        student_product.teacher_product_id = teacher_product.id
        await uow.teacher_assignment.create(
            student_product_id=student_product.id,
            teacher_product_id=teacher_product.id,
        )
        subject = await uow.product.find_subject_by_product(student_product.product_id)
        student = await uow.student.read_by_id(student_id=student_product.student_id)
        teacher = await uow.teacher.find_teacher_by_teacher_product(teacher_product.id)
        background_tasks.add_task(
            send_teacher_to_autopilot,
            target_url=subject.autopilot_url,
            student_vk_id=student.vk_id,
            teacher_vk_id=teacher.vk_id,
            teacher_type=student_product.teacher_type,  # type:ignore[arg-type]
        )
    student_product.expulsion_at = None
    student_product.offer_id = new_offer.id

    return await uow.student_product.update(
        StudentProduct.id == student_product.id,
        **asdict(student_product),
    )
