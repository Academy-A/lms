from dataclasses import asdict
from datetime import datetime

from fastapi import BackgroundTasks
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.autopilot import send_teacher_to_autopilot
from src.db.models import Offer, StudentProduct
from src.db.repositories.offer import OfferRepository
from src.db.repositories.product import ProductRepository
from src.db.repositories.soho import SohoRepository
from src.db.repositories.student import StudentRepository
from src.db.repositories.student_product import StudentProductRepository
from src.db.repositories.subject import SubjectRepository
from src.db.repositories.teacher import TeacherRepository
from src.db.repositories.teacher_assignment import TeacherAssignmentRepository
from src.db.repositories.teacher_product import TeacherProductRepository
from src.dto import NewStudentData
from src.enums import TeacherType
from src.exceptions.student import StudentNotFoundError, StudentProductNotFoundError


class DatabaseProvider:
    def __init__(
        self, session: AsyncSession, background_tasks: BackgroundTasks
    ) -> None:
        self.offer = OfferRepository(session=session)
        self.product = ProductRepository(session=session)
        self.soho = SohoRepository(session=session)
        self.student = StudentRepository(session=session)
        self.student_product = StudentProductRepository(session=session)
        self.subject = SubjectRepository(session=session)
        self.teacher = TeacherRepository(session=session)
        self.teacher_assignment = TeacherAssignmentRepository(session=session)
        self.teacher_product = TeacherProductRepository(session=session)
        self.background_tasks = background_tasks

    async def enroll_student(
        self, new_student: NewStudentData, offer_ids: list[int]
    ) -> StudentProduct:
        logger.info("Enroll student with data {data}", data=asdict(new_student))
        student = await self.student.read_by_vk_id(
            vk_id=new_student.vk_id,
        )
        if student is None:
            student = await self.student.create(
                first_name=new_student.first_name,
                last_name=new_student.last_name,
                vk_id=new_student.vk_id,
            )
            await self.soho.create(
                soho_id=new_student.soho_id,
                student_id=student.id,
                email=new_student.email,
            )
        offer_id = offer_ids[0]
        offer = await self.offer.read_by_id(offer_id=offer_id)
        old_student_product = await self.student_product.find_by_student_and_product(
            student_id=student.id,
            product_id=offer.product_id,
        )
        if old_student_product is not None:
            student_product = await self.enroll_student_again_by_offer(
                student_product=old_student_product, new_offer=offer
            )
        else:
            student_product = await self.enroll_student_by_offer_id(
                student_id=student.id,
                offer_id=offer_id,
            )
            if student_product.teacher_product_id and student_product.teacher_type:
                await self.send_teacher_assignment_to_autopilot(
                    product_id=student_product.product_id,
                    teacher_product_id=student_product.teacher_product_id,
                    student_id=student_product.student_id,
                    teacher_type=student_product.teacher_type,
                )
        return student_product

    async def enroll_student_by_offer_id(
        self, student_id: int, offer_id: int
    ) -> StudentProduct:
        offer = await self.offer.read_by_id(offer_id=offer_id)
        teacher_product = None
        if offer.teacher_type is not None:
            teacher_product = (
                await self.teacher_product.find_teacher_product_for_student_on_product(
                    product_id=offer.product_id,
                    teacher_type=offer.teacher_type,
                )
            )
        student_product = await self.student_product.create(
            student_id=student_id,
            product_id=offer.product_id,
            cohort=offer.cohort,
            offer_id=offer.id,
            teacher_type=offer.teacher_type,
            teacher_product_id=teacher_product.id if teacher_product else None,
        )
        if teacher_product is not None:
            await self.teacher_assignment.create(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
        return student_product

    async def enroll_student_again_by_offer(
        self, student_product: StudentProduct, new_offer: Offer
    ) -> StudentProduct:
        old_offer = await self.offer.read_by_id(student_product.offer_id)

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
            await self.teacher_assignment.expulse_from_teacher_assignment(
                student_product_id=student_product.id,
                teacher_product_id=student_product.teacher_product_id,  # type: ignore[arg-type]
            )
            student_product.teacher_product_id = None
            student_product.teacher_type = None
        elif not new_offer.is_alone:
            if not old_offer.is_alone:
                await self.teacher_assignment.expulse_from_teacher_assignment(
                    student_product_id=student_product.id,
                    teacher_product_id=student_product.teacher_product_id,  # type: ignore[arg-type]
                )
            teacher_product = (
                await self.teacher_product.find_teacher_product_for_student_on_product(
                    product_id=new_offer.product_id,
                    teacher_type=new_offer.teacher_type,  # type: ignore[arg-type]
                )
            )
            student_product.teacher_type = new_offer.teacher_type
            student_product.teacher_product_id = teacher_product.id
            await self.teacher_assignment.create(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
            await self.send_teacher_assignment_to_autopilot(
                product_id=student_product.product_id,
                teacher_product_id=teacher_product.id,
                student_id=student_product.student_id,
                teacher_type=student_product.teacher_type,  # type: ignore[arg-type]
            )
        student_product.expulsion_at = None
        student_product.offer_id = new_offer.id
        await self.student_product.save(student_product)
        return student_product

    async def expulse_student_by_offer_id(
        self,
        student_vk_id: int,
        offer_id: int,
    ) -> None:
        student = await self.student.read_by_vk_id(
            vk_id=student_vk_id,
        )
        if student is None:
            raise StudentNotFoundError
        offer = await self.offer.read_by_id(offer_id=offer_id)
        student_product = await self.student_product.find_by_student_and_product(
            student_id=student.id,
            product_id=offer.product_id,
        )
        if student_product is None:
            raise StudentProductNotFoundError
        now = datetime.now()
        await self.student_product.update(
            StudentProduct.id == student_product.id,
            expulsion_at=now,
            teacher_type=None,
            teacher_product_id=None,
        )
        if student_product.teacher_product_id is not None:
            await self.teacher_assignment.expulse_from_teacher_assignment(
                student_product_id=student_product.id,
                teacher_product_id=student_product.teacher_product_id,
            )
        return

    async def send_teacher_assignment_to_autopilot(
        self,
        product_id: int,
        teacher_product_id: int,
        student_id: int,
        teacher_type: TeacherType,
    ) -> None:
        student = await self.student.read_by_id(student_id=student_id)
        subject = await self.product.find_subject_by_product(product_id=product_id)
        teacher = await self.teacher.find_teacher_by_teacher_product(
            teacher_product_id=teacher_product_id,
        )
        self.background_tasks.add_task(
            send_teacher_to_autopilot,
            target_url=subject.autopilot_url,
            student_vk_id=student.vk_id,
            teacher_vk_id=teacher.vk_id,
            teacher_type=teacher_type,
        )
