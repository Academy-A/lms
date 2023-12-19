from http import HTTPStatus

from aiohttp.test_utils import TestClient
from freezegun import freeze_time

from tests.plugins.factories import SubjectFactory


async def test_unauthorized_user(api_client: TestClient) -> None:
    response = await api_client.get("/v1/subjects/1/")
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(api_client: TestClient) -> None:
    response = await api_client.get("/v1/subjects/1/", params={"token": "something"})
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


@freeze_time("2023-10-26")
async def test_successful_read(api_client: TestClient, token: str) -> None:
    subject = await SubjectFactory.create_async()
    response = await api_client.get(
        f"/v1/subjects/{subject.id}/", params={"token": token}
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "id": subject.id,
        "name": subject.name,
        "eng_name": subject.eng_name,
        "autopilot_url": subject.autopilot_url,
        "group_vk_url": subject.group_vk_url,
        "created_at": subject.created_at.isoformat(),
        "updated_at": subject.updated_at.isoformat(),
    }
