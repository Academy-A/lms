from datetime import datetime
from typing import Any, NoReturn

from loguru import logger
from sqlalchemy import ScalarResult, desc, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import (
    Offer,
    Soho,
    Student,
    StudentProduct,
    TeacherAssignment,
    TeacherProduct,
    TeacherType,
)
from src.db.repositories.base import Repository
from src.exceptions import (
    EntityNotFoundError,
    LMSError,
    StudentAlreadyEnrolldError,
    StudentProductNotFoundError,
    TeacherAssignmentNotFoundError,
    TeacherProductNotFoundError,
)


class StudentRepository(Repository[Student]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Student, session=session)

    async def read_student_by_vk_id(self, vk_id: int) -> Student | None:
        stmt = select(Student).where(Student.vk_id == vk_id)
        return (await self._session.scalars(stmt)).one_or_none()

    async def create_student(
        self,
        vk_id: int,
        first_name: str | None,
        last_name: str | None,
    ) -> Student:
        stmt = (
            insert(Student)
            .values(vk_id=vk_id, first_name=first_name or "", last_name=last_name or "")
            .returning(Student)
        )
        try:
            result: ScalarResult[Student] = await self._session.scalars(
                select(Student).from_statement(stmt),
            )
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    async def create_soho_account(
        self,
        soho_id: int,
        email: str,
        student_id: int,
    ) -> Soho:
        stmt = (
            insert(Soho)
            .values(
                id=soho_id,
                email=email,
                student_id=student_id,
            )
            .returning(Soho)
        )
        try:
            result: ScalarResult[Soho] = await self._session.scalars(
                select(Soho).from_statement(stmt),
            )
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    async def enroll_student_to_product(
        self,
        student_id: int,
        offer_id: int,
    ) -> StudentProduct:
        student_product = await self.find_student_product_by_offer_id(
            student_id=student_id,
            offer_id=offer_id,
        )
        if student_product is not None:
            raise StudentAlreadyEnrolldError
        offer = await self._session.get(Offer, offer_id)
        if offer is None:
            raise EntityNotFoundError

        teacher_product = None
        if offer.teacher_type is not None:
            teacher_product = await self.find_teacher_for_student_on_product(
                product_id=offer.product_id,
                teacher_type=offer.teacher_type,
            )
        student_product_data: dict[str, Any] = {
            "student_id": student_id,
            "product_id": offer.product_id,
            "offer_id": offer.id,
            "cohort": offer.cohort,
            "teacher_product_id": None,
        }
        if teacher_product and offer.teacher_type is not None:
            student_product_data["teacher_product_id"] = teacher_product.id
            student_product_data["teacher_type"] = offer.teacher_type
        stmt = (
            insert(StudentProduct)
            .values(**student_product_data)
            .returning(StudentProduct)
        )
        try:
            result: ScalarResult[StudentProduct] = await self._session.scalars(
                select(Soho).from_statement(stmt),
            )
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            student_product = result.one()
            if teacher_product is not None:
                await self.assign_teacher(
                    student_product_id=student_product.id,
                    teacher_product_id=teacher_product.id,
                )

            return student_product

    async def find_student_product_by_offer_id(
        self,
        student_id: int,
        offer_id: int,
    ) -> StudentProduct | None:
        stmt = select(StudentProduct).where(
            StudentProduct.offer_id == offer_id,
            StudentProduct.student_id == student_id,
        )
        return (await self._session.scalars(stmt)).one_or_none()

    async def find_teacher_for_student_on_product(
        self,
        product_id: int,
        teacher_type: TeacherType,
    ) -> TeacherProduct:
        stmt = (
            select(TeacherProduct)
            .where(
                TeacherProduct.product_id == product_id,
                TeacherProduct.type == teacher_type,
                TeacherProduct.max_students > 0,
            )
            .order_by(desc(TeacherProduct.rating_coef))
            .limit(1)
        )
        teacher_product = (await self._session.scalars(stmt)).first()
        if teacher_product is None:
            raise TeacherProductNotFoundError
        return teacher_product

    async def assign_teacher(
        self,
        teacher_product_id: int,
        student_product_id: int,
    ) -> TeacherAssignment:
        stmt = (
            insert(TeacherAssignment)
            .values(
                teacher_product_id=teacher_product_id,
                student_product_id=student_product_id,
            )
            .returning(TeacherAssignment)
        )
        try:
            result: ScalarResult[TeacherAssignment] = await self._session.scalars(
                select(TeacherAssignment).from_statement(stmt),
            )
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            self._raise_error(e)
        else:
            return result.one()

    async def remove_teacher(
        self,
        student_product_id: int,
        teacher_product_id: int,
    ) -> None:
        now = datetime.now()
        await self._update_teacher_assignment(
            TeacherAssignment.student_product_id == student_product_id,
            TeacherAssignment.teacher_product_id == teacher_product_id,
            TeacherAssignment.removed_at.is_(None),
            removed_at=now,
        )

    async def expell_from_product(
        self,
        student_product_id: int,
        teacher_product_id: int | None,
    ) -> None:
        now = datetime.now()
        await self._update_student_product(
            StudentProduct.id == student_product_id,
            expulsion_at=now,
            mentor_id=None,
            curator_id=None,
        )
        if teacher_product_id is not None:
            await self.remove_teacher(
                student_product_id=student_product_id,
                teacher_product_id=teacher_product_id,
            )

    async def _update_student_product(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> StudentProduct:
        stmt = (
            update(StudentProduct)
            .where(*args)
            .values(**kwargs)
            .returning(StudentProduct)
        )
        try:
            result = await self._session.scalars(
                select(StudentProduct).from_statement(stmt),
            )
            await self._session.commit()
            return result.one()
        except NoResultFound as e:
            await self._session.rollback()
            raise StudentProductNotFoundError from e

    async def _update_teacher_assignment(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> TeacherAssignment:
        stmt = (
            update(TeacherAssignment)
            .where(*args)
            .values(**kwargs)
            .returning(TeacherAssignment)
        )
        try:
            result = await self._session.scalars(
                select(TeacherAssignment).from_statement(stmt),
            )
            await self._session.commit()
            return result.one()
        except NoResultFound as e:
            await self._session.rollback()
            raise TeacherAssignmentNotFoundError from e

    def _raise_error(self, e: DBAPIError) -> NoReturn:
        logger.exception(
            "Occured exc",
        )
        raise LMSError from e
