from fastapi import APIRouter, BackgroundTasks, Depends

from lms.api.deps import UnitOfWorkMarker
from lms.api.services import token_required
from lms.api.v1.schemas import StatusResponseSchema
from lms.api.v1.student.schemas import (
    ChangeVKIDSchema,
    EnrollStudentSchema,
    ExpulsionStudentSchema,
    GradeTeacherSchema,
    ReadStudentProductSchema,
    ReadStudentSchema,
)
from lms.api.v1.student.utils import parse_soho_flow_id
from lms.db.uow import UnitOfWork
from lms.dto import NewStudentData
from lms.services.change_vk_id import change_student_vk_id_by_soho_id
from lms.services.enroll_student import enroll_student
from lms.services.expulse_student import expulse_student_by_offer_id
from lms.services.grade_teacher import grade_teacher

router = APIRouter(
    prefix="/students",
    tags=["Students"],
    dependencies=[Depends(token_required)],
)


@router.post("/")
async def enroll_student_route(
    enrollment: EnrollStudentSchema,
    background_tasks: BackgroundTasks,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> ReadStudentProductSchema:
    _, soho_flow_id = parse_soho_flow_id(enrollment.student.raw_soho_flow_id)
    async with uow:
        student_product = await enroll_student(
            uow=uow,
            background_tasks=background_tasks,
            new_student=NewStudentData(
                vk_id=enrollment.student.vk_id,
                soho_id=enrollment.student.soho_id,
                email=enrollment.student.email,
                first_name=enrollment.student.first_name,
                last_name=enrollment.student.last_name,
                flow_id=soho_flow_id,
            ),
            offer_ids=enrollment.offer_ids,
        )
        await uow.commit()
    return ReadStudentProductSchema.model_validate(student_product)


@router.post("/expulse")
async def expulsion_student_route(
    expulsion_data: ExpulsionStudentSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> StatusResponseSchema:
    offer_id, soho_flow_id = parse_soho_flow_id(expulsion_data.raw_soho_flow_id)
    async with uow:
        await expulse_student_by_offer_id(
            uow=uow,
            student_vk_id=expulsion_data.vk_id,
            offer_id=offer_id,
        )
        await uow.commit()
    return StatusResponseSchema(
        ok=True,
        status_code=200,
        message="Student was expulsed",
    )


@router.get(
    "/{student_id}",
    response_model=ReadStudentSchema,
    responses={
        403: {"model": StatusResponseSchema},
        404: {"model": StatusResponseSchema},
    },
)
async def read_student_by_id_route(
    student_id: int,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> ReadStudentSchema:
    async with uow:
        student = await uow.student.read_by_id(student_id=student_id)
    return ReadStudentSchema.model_validate(student)


@router.post("/soho/{soho_id}/change-vk-id", response_model=ReadStudentSchema)
async def change_vk_id_by_soho_id_route(
    soho_id: int,
    vk_id_data: ChangeVKIDSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> ReadStudentSchema:
    async with uow:
        student = await change_student_vk_id_by_soho_id(
            uow=uow,
            soho_id=soho_id,
            vk_id=vk_id_data.vk_id,
        )
        await uow.commit()
    return ReadStudentSchema.model_validate(student)


@router.post("/soho/{soho_id}/grade-teacher", response_model=StatusResponseSchema)
async def grade_teacher_route(
    soho_id: int,
    grade_data: GradeTeacherSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> StatusResponseSchema:
    async with uow:
        await grade_teacher(
            uow=uow,
            soho_id=soho_id,
            product_id=grade_data.product_id,
            grade=grade_data.grade,
        )
        await uow.commit()
    return StatusResponseSchema(
        ok=True,
        status_code=200,
        message="Teacher was graded",
    )