from dirty_equals import IsListOrTuple

from lms.db.repositories.reviewer import ReviewerRepository
from lms.db.uow import UnitOfWork
from lms.generals.models.reviewer import Reviewer


async def test_get_list_by_subject_id__subject_unknown(
    uow: UnitOfWork,
):
    async with uow:
        result = await uow.reviewer.get_list_by_subject_id(subject_id=1)
    assert result == IsListOrTuple(length=0)


async def test_get_list_by_subject_id__ok(
    reviewer_repository: ReviewerRepository,
    create_subject,
    create_reviewer,
):
    subject = await create_subject()
    reviewer = await create_reviewer(subject_id=subject.id)

    result = await reviewer_repository.get_list_by_subject_id(subject_id=subject.id)
    assert result == IsListOrTuple(Reviewer.model_validate(reviewer), length=1)


async def test_get_list_by_subject_id__filter_inactive(
    reviewer_repository: ReviewerRepository,
    create_subject,
    create_reviewer,
):
    subject = await create_subject()
    await create_reviewer(subject_id=subject.id, is_active=False)

    result = await reviewer_repository.get_list_by_subject_id(subject_id=subject.id)
    assert result == IsListOrTuple(length=0)


async def test_get_list_by_subject_id__filter_subject(
    reviewer_repository: ReviewerRepository,
    create_subject,
    create_reviewer,
):
    subject = await create_subject()
    await create_reviewer(subject_id=subject.id)

    result = await reviewer_repository.get_list_by_subject_id(subject_id=subject.id + 1)
    assert result == IsListOrTuple(length=0)
