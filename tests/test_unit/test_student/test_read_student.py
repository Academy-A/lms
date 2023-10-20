import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import StudentFactory

pytestmark = [pytest.mark.asyncio]


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.get(f"v1/students/1")
    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "status_code": 401,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.get(f"v1/students/1", params={"token": "something"})
    assert response.status_code == 403
    assert response.json() == {
        "ok": False,
        "status_code": 403,
        "message": "Token not recognized",
    }


async def test_student_not_found(client: AsyncClient, token: str) -> None:
    response = await client.get(f"v1/students/0", params={"token": token})
    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "status_code": 404,
        "message": "Student not found",
    }


async def test_successful_read(
    client: AsyncClient, session: AsyncSession, token: str
) -> None:
    students = await StudentFactory.create_batch_async(3)
    for student in students:
        response = await client.get(
            f"v1/students/{student.id}", params={"token": token}
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "vk_id": student.vk_id,
        }
