from http import HTTPStatus

from fastapi import APIRouter, Depends, Path
from pydantic import PositiveInt

from lms.adapters.db.uow import UnitOfWork
from lms.generals.models.student import NewStudent, Student
from lms.generals.models.student_product import StudentProduct
from lms.logic.change_vk_id import change_student_vk_id_by_soho_id
from lms.logic.enroll_student import Enroller
from lms.logic.expulse_student import expulse_student_by_offer_id
from lms.logic.grade_teacher import grade_teacher
from lms.presentation.rest.api.auth import token_required
from lms.presentation.rest.api.deps import EnrollerMarker, UnitOfWorkMarker
from lms.presentation.rest.api.v1.schemas import StatusResponseSchema
from lms.presentation.rest.api.v1.student.schemas import (
    ChangeTeacherSchema,
    ChangeVKIDSchema,
    EnrollStudentSchema,
    ExpulsionStudentSchema,
    GradeTeacherSchema,
)

router = APIRouter(
    prefix="/students",
    tags=["Students"],
    dependencies=[Depends(token_required)],
)


@router.post("/")
async def enroll_student_route(
    enrollment: EnrollStudentSchema,
    enroller: Enroller = Depends(EnrollerMarker),
) -> StudentProduct:
    async with enroller.uow.start():
        student_product = await enroller.enroll_student(
            new_student=NewStudent(
                vk_id=enrollment.student.vk_id,
                soho_id=enrollment.student.soho_id,
                email=enrollment.student.email,
                first_name=enrollment.student.first_name,
                last_name=enrollment.student.last_name,
                flow_id=enrollment.student.raw_soho_flow_id.flow_id,  # type: ignore[union-attr]
            ),
            offer_ids=enrollment.offer_ids,
        )
        await enroller.uow.commit()
    return student_product


@router.post("/expulse/")
async def expulsion_student_route(
    expulsion_data: ExpulsionStudentSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> StatusResponseSchema:
    async with uow.start():
        await expulse_student_by_offer_id(
            uow=uow,
            student_vk_id=expulsion_data.vk_id,
            product_id=expulsion_data.product_id,
        )
        await uow.commit()
    return StatusResponseSchema(
        ok=True,
        status_code=HTTPStatus.OK,
        message="Student was expulsed from product",
    )


@router.post("/change-teacher/")
async def change_teacher_product(
    change_teacher_data: ChangeTeacherSchema,
    enroller: Enroller = Depends(EnrollerMarker),
) -> StatusResponseSchema:
    async with enroller.uow.start():
        await enroller.change_teacher_for_student(
            product_id=change_teacher_data.product_id,
            student_vk_id=change_teacher_data.student_vk_id,
            teacher_vk_id=change_teacher_data.teacher_vk_id,
        )
        await enroller.uow.commit()
    return StatusResponseSchema(
        ok=True,
        status_code=HTTPStatus.OK,
        message="Teacher was changed for student",
    )


@router.get(
    "/{student_id}/",
    response_model=Student,
    responses={
        HTTPStatus.OK: {"model": Student},
        HTTPStatus.FORBIDDEN: {"model": StatusResponseSchema},
        HTTPStatus.NOT_FOUND: {"model": StatusResponseSchema},
    },
)
async def read_student_by_id_route(
    student_id: PositiveInt = Path(),
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> Student:
    async with uow.start():
        student = await uow.student.read_by_id(student_id=student_id)
    return student


@router.post("/soho/{soho_id}/change-vk-id/", response_model=Student)
async def change_vk_id_by_soho_id_route(
    soho_id: PositiveInt,
    vk_id_data: ChangeVKIDSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> Student:
    async with uow.start():
        student = await change_student_vk_id_by_soho_id(
            uow=uow,
            soho_id=soho_id,
            vk_id=vk_id_data.vk_id,
        )
        await uow.commit()
    return student


@router.post("/soho/{soho_id}/grade-teacher/", response_model=StatusResponseSchema)
async def grade_teacher_route(
    soho_id: PositiveInt,
    grade_data: GradeTeacherSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> StatusResponseSchema:
    async with uow.start():
        await grade_teacher(
            uow=uow,
            soho_id=soho_id,
            product_id=grade_data.product_id,
            grade=grade_data.grade,
        )
        await uow.commit()
    return StatusResponseSchema(
        ok=True,
        status_code=HTTPStatus.OK,
        message="Teacher was graded",
    )
