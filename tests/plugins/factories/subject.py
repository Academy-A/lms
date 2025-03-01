from collections.abc import Callable

import factory
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Subject


class SubjectPropertiesFactory(factory.Factory):
    class Meta:
        model = dict

    eng_name = "subject-1"
    enroll_autopilot_url = "http://example.com/"
    group_vk_url = "http://example.com/"
    check_spreadsheet_id = "1"
    check_drive_folder_id = "1"
    check_regular_notification_folder_ids = []
    check_subscription_notification_folder_ids = []
    check_additional_notification_folder_ids = []
    check_file_regex = "Математика"


class SubjectFactory(factory.Factory):
    class Meta:
        model = Subject

    id = factory.Sequence(lambda n: n + 1)
    name = "Subject-1"
    properties = factory.SubFactory(SubjectPropertiesFactory)


@pytest.fixture
def create_subject(session: AsyncSession) -> Callable:
    async def _factory(**kwargs):
        subject = SubjectFactory(**kwargs)
        session.add(subject)
        await session.commit()
        await session.flush(subject)
        return subject

    return _factory
