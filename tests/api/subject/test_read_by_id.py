from http import HTTPStatus

from aiohttp.test_utils import TestClient


async def test_unauthorized_user(api_client: TestClient) -> None:
    response = await api_client.get("/v1/subjects/1/")
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(api_client: TestClient) -> None:
    response = await api_client.get(
        "/v1/subjects/1/",
        params={"token": "something"},
    )
    assert response.status == HTTPStatus.FORBIDDEN
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_subject_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.get("/v1/subjects/0/", params={"token": token})
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Subject not found",
    }


async def test_successful_read(
    api_client: TestClient,
    token: str,
    create_subject,
) -> None:
    subject = await create_subject()
    response = await api_client.get(
        f"/v1/subjects/{subject.id}/",
        params={"token": token},
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "id": subject.id,
        "name": subject.name,
        "created_at": subject.created_at.isoformat(),
        "updated_at": subject.updated_at.isoformat(),
        "properties": {
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
        },
    }
