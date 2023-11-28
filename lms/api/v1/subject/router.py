from fastapi import APIRouter, Depends, Query

from lms.api.auth import token_required
from lms.api.deps import UnitOfWorkMarker
from lms.api.v1.subject.schema import ReadSubjectSchema, SubjectPageSchema
from lms.db.uow import UnitOfWork

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
    dependencies=[Depends(token_required)],
)


@router.get("/")
async def read_subjects(
    page: int = Query(gt=0, default=1),
    page_size: int = Query(gt=0, le=100, default=20),
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> SubjectPageSchema:
    async with uow:
        pagination = await uow.subject.paginate(
            page=page,
            page_size=page_size,
        )
    return SubjectPageSchema.from_pagination(pagination=pagination)


@router.get("/{subject_id}/")
async def read_subject_by_id(
    subject_id: int,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> ReadSubjectSchema:
    async with uow:
        subject = await uow.subject.read_by_id(subject_id=subject_id)
    return ReadSubjectSchema.model_validate(subject)
