from fastapi import APIRouter, Depends, Query

from lms.db.uow import UnitOfWork
from lms.generals.models.pagination import Pagination
from lms.generals.models.subject import ShortSubject, Subject
from lms.rest.api.auth import token_required
from lms.rest.api.deps import UnitOfWorkMarker

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
    dependencies=[Depends(token_required)],
)


@router.get("/")
async def read_list(
    page: int = Query(gt=0, default=1),
    page_size: int = Query(gt=0, le=100, default=20),
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> Pagination[ShortSubject]:
    async with uow.start():
        pagination = await uow.subject.paginate(
            page=page,
            page_size=page_size,
        )
    return pagination


@router.get("/{subject_id}/")
async def read_by_id(
    subject_id: int,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> Subject:
    async with uow.start():
        subject = await uow.subject.read_by_id(subject_id=subject_id)
    return subject
