from http import HTTPStatus

from freezegun import freeze_time
from httpx import AsyncClient

from tests.factories import SubjectFactory


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.get("/v1/subjects/1/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/v1/subjects/1/", params={"token": "something"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_subject_not_found(client: AsyncClient, token: str) -> None:
    response = await client.get("/v1/subjects/0/", params={"token": token})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Subject not found",
    }


@freeze_time("2023-10-26")
async def test_successful_read(client: AsyncClient, token: str) -> None:
    subject = await SubjectFactory.create_async()
    response = await client.get(f"/v1/subjects/{subject.id}/", params={"token": token})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": subject.id,
        "name": subject.name,
        "eng_name": subject.eng_name,
        "autopilot_url": subject.autopilot_url,
        "group_vk_url": subject.group_vk_url,
        "created_at": subject.created_at.isoformat(timespec="seconds"),
        "updated_at": subject.updated_at.isoformat(timespec="seconds"),
    }
