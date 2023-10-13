from fastapi import APIRouter, BackgroundTasks, Depends


from src.api.deps import DatabaseProviderMarker
from src.api.services import token_required
from src.api.v1.schemas import StatusResponseSchema
from src.api.v1.student.schemas import (
    ChangeVKIDSchema,
    EnrollStudentSchema,
    ExpulsionStudentSchema,
    ReadStudentProductSchema,
    ReadStudentSchema,
)
from src.db.models import Student
from src.db.provider import DatabaseProvider
from src.dto import NewStudentData

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
    student_product = await provider.enroll_student(
        new_student=NewStudentData(
            vk_id=enroll_student.student.vk_id,
            soho_id=enroll_student.student.soho_id,
            email=enroll_student.student.email,
            first_name=enroll_student.student.first_name,
            last_name=enroll_student.student.last_name,
            flow_id=enroll_student.student.flow_id,
        ),
        offer_ids=enroll_student.offer_ids,
    )
    return ReadStudentProductSchema.model_validate(student_product)


@router.post("/expulse")
async def expulsion_student_route(
    expulsion_data: ExpulsionStudentSchema,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> StatusResponseSchema:
    await provider.expulse_student_by_offer_id(
        student_vk_id=expulsion_data.vk_id,
        offer_id=expulsion_data.offer_id,
    )
    return StatusResponseSchema(
        ok=True,
        status_code=200,
        message="Student was expulsed",
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


@router.post("/soho/{soho_id}/change-vk-id", response_model=ReadStudentSchema)
async def change_vk_id_by_soho_id(
    soho_id: int,
    vk_id_data: ChangeVKIDSchema,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> ReadStudentSchema:
    soho = await provider.soho.read_by_id(soho_id=soho_id)
    student = await provider.student.update(
        Student.id == soho.student_id,
        vk_id=vk_id_data.vk_id,
    )
    return ReadStudentSchema.model_validate(student)
