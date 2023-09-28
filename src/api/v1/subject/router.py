from fastapi import APIRouter, Depends, Query

from src.api.deps import DatabaseProviderMarker
from src.api.services import token_required
from src.api.v1.subject.schema import ReadSubjectSchema, SubjectPageSchema
from src.db.provider import DatabaseProvider

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
    dependencies=[Depends(token_required)],
)


@router.get("/")
async def read_subjects(
    page: int = Query(gt=0, default=1),
    page_size: int = Query(gt=0, le=100, default=20),
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> SubjectPageSchema:
    pagination = await provider.subject.paginate(
        page=page,
        page_size=page_size,
    )
    return SubjectPageSchema.from_pagination(pagination=pagination)


@router.get("/{subject_id}/")
async def read_subject_by_id(
    subject_id: int,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> ReadSubjectSchema:
    subject = await provider.subject.read_by_id(subject_id=subject_id)
    return ReadSubjectSchema.model_validate(subject)
