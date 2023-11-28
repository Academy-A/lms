from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories import StudentFactory

pytestmark = [pytest.mark.asyncio]


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.get("/v1/students/1/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/v1/students/1/", params={"token": "something"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_student_not_found(client: AsyncClient, token: str) -> None:
    response = await client.get("/v1/students/0/", params={"token": token})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Student not found",
    }


async def test_successful_read(client: AsyncClient, token: str) -> None:
    student = await StudentFactory.create_async()
    response = await client.get(f"/v1/students/{student.id}/", params={"token": token})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "vk_id": student.vk_id,
    }
