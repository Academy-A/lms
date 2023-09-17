from fastapi import APIRouter, BackgroundTasks, Depends
from loguru import logger

from src.api.deps import DatabaseProviderMarker
from src.api.services import token_required
from src.api.v1.schemas import StatusResponseSchema
from src.api.v1.student.schemas import (
    EnrollStudentSchema,
    ExpulsionStudentSchema,
    ReadStudentProductSchema,
    ReadStudentSchema,
)
from src.clients.autopilot import send_teacher_to_autopilot
from src.db.provider import DatabaseProvider
from src.exceptions import StudentNotFoundError, StudentProductNotFoundError

router = APIRouter(
    prefix="/students",
    tags=["Students"],
    dependencies=[Depends(token_required)],
)


@router.post("/")
async def enroll_student_route(
    enroll_student: EnrollStudentSchema,
    background_tasks: BackgroundTasks,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> ReadStudentProductSchema:
    logger.info("Enroll student with data {data}", data=enroll_student.model_dump())
    student = await provider.student.read_by_vk_id(
        vk_id=enroll_student.student.vk_id,
    )
    if student is None:
        student = await provider.student.create_student(
            first_name=enroll_student.student.first_name,
            last_name=enroll_student.student.last_name,
            vk_id=enroll_student.student.vk_id,
        )
        await provider.student.create_soho_account(
            student_id=student.id,
            soho_id=enroll_student.student.soho_id,
            email=enroll_student.student.email,
        )
    student_product = await provider.student.enroll_student_to_product(
        student_id=student.id,
        offer_id=enroll_student.offer_ids[0],
    )
    if student_product.teacher_product_id and student_product.teacher_type:
        subject = await provider.product.find_subject_by_product(
            product_id=student_product.product_id,
        )
        teacher = await provider.teacher.find_teacher_by_teacher_product(
            teacher_product_id=student_product.teacher_product_id,
        )
        background_tasks.add_task(
            send_teacher_to_autopilot,
            target_url=subject.autopilot_url,
            student_vk_id=student.vk_id,
            teacher_vk_id=teacher.vk_id,
            teacher_type=student_product.teacher_type,
        )
    return ReadStudentProductSchema.model_validate(student_product)


@router.post("/expulsion")
async def expulsion_student_route(
    expulsion_data: ExpulsionStudentSchema,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> StatusResponseSchema:
    student = await provider.student.read_by_vk_id(
        vk_id=expulsion_data.vk_id,
    )
    if student is None:
        raise StudentNotFoundError
    student_product = await provider.student.find_student_product_by_offer_id(
        student_id=student.id,
        offer_id=expulsion_data.offer_id,
    )
    if student_product is None:
        raise StudentProductNotFoundError
    await provider.student.expell_from_product(
        student_product_id=student_product.id,
        teacher_product_id=student_product.teacher_product_id,
    )
    return StatusResponseSchema(
        ok=True,
        status_code=200,
        message="Student was expelled",
    )


@router.get(
    "/{student_id}",
    response_model=ReadStudentSchema,
    responses={
        203: {"model": StatusResponseSchema},
        404: {"model": StatusResponseSchema},
    },
)
async def read_student_by_id(
    student_id: int,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> ReadStudentSchema:
    student = await provider.student.read_by_id(student_id=student_id)
    return ReadStudentSchema.model_validate(student)
