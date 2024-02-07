import logging
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime

from fastapi import BackgroundTasks

from lms.clients.autopilot import Autopilot
from lms.clients.telegram import Telegram
from lms.db.uow import UnitOfWork
from lms.exceptions import (
    StudentNotFoundError,
    StudentProductNotFoundError,
)
from lms.generals.models.offer import Offer
from lms.generals.models.student import NewStudent
from lms.generals.models.student_product import StudentProduct

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Enroller:
    uow: UnitOfWork
    autopilot: Autopilot
    telegram: Telegram
    background_tasks: BackgroundTasks

    async def enroll_student(
        self,
        new_student: NewStudent,
        offer_ids: Sequence[int],
    ) -> StudentProduct:
        log.info("Enroll student with data %s", asdict(new_student))
        student = await self.uow.student.read_by_vk_id(vk_id=new_student.vk_id)
        if student is None:
            student = await self.uow.student.create(
                first_name=new_student.first_name,
                last_name=new_student.last_name,
                vk_id=new_student.vk_id,
            )
            await self.uow.soho.create(
                soho_id=new_student.soho_id,
                student_id=student.id,
                email=new_student.email,
            )
        offer_id = offer_ids[0]
        offer = await self.uow.offer.read_by_id(offer_id=offer_id)
        old_student_product = (
            await self.uow.student_product.find_by_student_and_product(
                student_id=student.id,
                product_id=offer.product_id,
            )
        )
        if old_student_product is not None:
            return await self._enroll_student_again_by_offer(
                student_product=old_student_product,
                new_offer=offer,
            )
        flow = await self.uow.flow.get_by_soho_id(new_student.flow_id)
        student_product = await self._enroll_student_by_offer_id(
            student_id=student.id,
            offer_id=offer_id,
            flow_id=flow.id if flow else None,
        )
        if student_product.teacher_product_id and student_product.teacher_type:
            subject = await self.uow.subject.find_by_product(
                product_id=student_product.product_id,
            )
            teacher = await self.uow.teacher.find_teacher_by_teacher_product(
                teacher_product_id=student_product.teacher_product_id,
            )
            self.background_tasks.add_task(
                self.autopilot.send_teacher,
                target_path=subject.enroll_autopilot_url,
                student_vk_id=student.vk_id,
                teacher_vk_id=teacher.vk_id,
                teacher_type=student_product.teacher_type,
            )
            teacher_product = await self.uow.teacher_product.read_by_id(
                student_product.teacher_product_id
            )
            if (
                await self.uow.student_product.calculate_active_students(
                    teacher_product.id
                )
                > teacher_product.max_students
            ):
                self.background_tasks.add_task(
                    self.telegram.teacher_overflow_alert,
                    max_students=teacher_product.max_students,
                    name=teacher.name,
                    vk_id=teacher.vk_id,
                    product_id=teacher_product.product_id,
                )
        return student_product

    async def _enroll_student_by_offer_id(
        self,
        student_id: int,
        offer_id: int,
        flow_id: int | None = None,
    ) -> StudentProduct:
        offer = await self.uow.offer.read_by_id(offer_id=offer_id)
        teacher_product = None
        if offer.teacher_type is not None:
            teacher_product = await self.uow.teacher_product.get_for_enroll(
                product_id=offer.product_id,
                teacher_type=offer.teacher_type,
                flow_id=flow_id,
            )
        student_product = await self.uow.student_product.create(
            student_id=student_id,
            product_id=offer.product_id,
            cohort=offer.cohort,
            offer_id=offer.id,
            teacher_type=offer.teacher_type,
            teacher_product_id=teacher_product.id if teacher_product else None,
            flow_id=flow_id,
        )
        if teacher_product is not None:
            await self.uow.teacher_assignment.create(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
        return student_product

    async def _enroll_student_again_by_offer(
        self,
        student_product: StudentProduct,
        new_offer: Offer,
    ) -> StudentProduct:
        teacher_product = None
        old_offer = await self.uow.offer.read_by_id(student_product.offer_id)
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
            await self.uow.teacher_assignment.expulse_student_safety(
                student_product_id=student_product.id,
                teacher_product_id=student_product.teacher_product_id,  # type: ignore[arg-type]
            )
            student_product.teacher_product_id = None
            student_product.teacher_type = None
        elif not new_offer.is_alone:
            if not old_offer.is_alone:
                await self.uow.teacher_assignment.expulse_student_safety(
                    student_product_id=student_product.id,
                    teacher_product_id=student_product.teacher_product_id,  # type: ignore[arg-type]
                )
            teacher_product = await self.uow.teacher_product.get_for_enroll(
                product_id=new_offer.product_id,
                teacher_type=new_offer.teacher_type,  # type: ignore[arg-type]
                flow_id=student_product.flow_id,
            )
            await self.uow.teacher_assignment.create(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
            subject = await self.uow.subject.find_by_product(student_product.product_id)
            student = await self.uow.student.read_by_id(
                student_id=student_product.student_id
            )
            teacher = await self.uow.teacher.find_teacher_by_teacher_product(
                teacher_product.id
            )
            self.background_tasks.add_task(
                self.autopilot.send_teacher,
                target_path=subject.enroll_autopilot_url,
                student_vk_id=student.vk_id,
                teacher_vk_id=teacher.vk_id,
                teacher_type=new_offer.teacher_type,  # type:ignore[arg-type]
            )
            if (
                await self.uow.student_product.calculate_active_students(
                    teacher_product.id
                )
                > teacher_product.max_students
            ):
                self.background_tasks.add_task(
                    self.telegram.teacher_overflow_alert,
                    max_students=teacher_product.max_students,
                    name=teacher.name,
                    vk_id=teacher.vk_id,
                    product_id=teacher_product.product_id,
                )
        teacher_product_id = (
            teacher_product.id
            if teacher_product
            else student_product.teacher_product_id
        )
        return await self.uow.student_product.update(
            student_product_id=student_product.id,
            expulsion_at=None,
            offer_id=new_offer.id,
            teacher_type=new_offer.teacher_type,
            teacher_product_id=teacher_product_id,
        )

    async def change_teacher_for_student(
        self,
        product_id: int,
        student_vk_id: int,
        teacher_vk_id: int,
    ) -> StudentProduct:
        student = await self.uow.student.read_by_vk_id(vk_id=student_vk_id)
        if student is None:
            raise StudentNotFoundError
        teacher = await self.uow.teacher.read_by_vk_id(vk_id=teacher_vk_id)
        product = await self.uow.product.read_by_id(product_id=product_id)
        subject = await self.uow.subject.find_by_product(product_id=product.id)
        student_product = await self.uow.student_product.find_by_student_and_product(
            student_id=student.id,
            product_id=product.id,
        )
        if student_product is None:
            raise StudentProductNotFoundError

        teacher_product = await self.uow.teacher_product.find_by_teacher_and_product(
            teacher_id=teacher.id,
            product_id=product.id,
        )
        if (
            student_product.teacher_product_id is not None
            and student_product.teacher_product_id != teacher_product.id
        ):
            await self.uow.teacher_assignment.expulse_student_safety(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
        if student_product.teacher_product_id != teacher_product.id:
            student_product = await self.uow.student_product.update(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
                teacher_type=teacher_product.type,
            )
            await self.uow.teacher_assignment.create(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
                assignment_at=datetime.now(),
            )
        self.background_tasks.add_task(
            self.autopilot.send_teacher,
            target_path=subject.enroll_autopilot_url,
            student_vk_id=student.vk_id,
            teacher_vk_id=teacher.vk_id,
            teacher_type=teacher_product.type,
        )
        if (
            await self.uow.student_product.calculate_active_students(teacher_product.id)
            > teacher_product.max_students
        ):
            self.background_tasks.add_task(
                self.telegram.teacher_overflow_alert,
                max_students=teacher_product.max_students,
                name=teacher.name,
                vk_id=teacher.vk_id,
                product_id=teacher_product.product_id,
            )
        return student_product
