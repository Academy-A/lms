from http import HTTPStatus

from aiohttp.test_utils import TestClient
from dirty_equals import IsPartialDict


def api_url(subject_id: int) -> str:
    return f"/v1/subjects/{subject_id}/"


async def test_unauthorized_user(api_client: TestClient) -> None:
    response = await api_client.get(api_url(1))
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(api_client: TestClient) -> None:
    response = await api_client.get(
        api_url(1),
        params={"token": "something"},
    )
    assert response.status == HTTPStatus.FORBIDDEN
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_subject_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.get(api_url(0), params={"token": token})
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Subject not found",
    }


async def test_read_status_ok(
    api_client: TestClient,
    token: str,
    create_subject,
) -> None:
    subject = await create_subject()
    response = await api_client.get(
        api_url(subject.id),
        params={"token": token},
    )
    assert response.status == HTTPStatus.OK


async def test_format_main_ok(
    api_client: TestClient,
    token: str,
    create_subject,
):
    subject = await create_subject()
    response = await api_client.get(
        api_url(subject.id),
        params={"token": token},
    )
    assert await response.json() == IsPartialDict(
        {
            "id": subject.id,
            "name": subject.name,
            "created_at": subject.created_at.isoformat(),
            "updated_at": subject.updated_at.isoformat(),
            "properties": IsPartialDict({}),
        }
    )


async def test_format_properties_ok(
    api_client: TestClient,
    token: str,
    create_subject,
):
    subject = await create_subject()
    response = await api_client.get(
        api_url(subject.id),
        params={"token": token},
    )

    assert (await response.json())["properties"] == {
        "eng_name": subject.properties["eng_name"],
        "enroll_autopilot_url": subject.properties["enroll_autopilot_url"],
        "group_vk_url": subject.properties["group_vk_url"],
        "check_drive_folder_id": subject.properties["check_drive_folder_id"],
        "check_spreadsheet_id": subject.properties["check_spreadsheet_id"],
        "check_file_regex": subject.properties["check_file_regex"],
        "check_regular_notification_folder_ids": subject.properties[
            "check_regular_notification_folder_ids"
        ],
        "check_subscription_notification_folder_ids": subject.properties[
            "check_subscription_notification_folder_ids"
        ],
        "check_additional_notification_folder_ids": subject.properties[
            "check_additional_notification_folder_ids"
        ],
    }
