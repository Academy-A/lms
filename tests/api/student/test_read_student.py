from collections.abc import Callable
from http import HTTPStatus

from aiohttp.test_utils import TestClient


async def test_unauthorized_user_check_status(api_client: TestClient) -> None:
    response = await api_client.get("/v1/students/1/")
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_user_check_response(
    api_client: TestClient,
    unauthorized_resp: dict[str, int | str],
) -> None:
    response = await api_client.get("/v1/students/1/")
    assert await response.json() == unauthorized_resp


async def test_invalid_token_check_status(api_client: TestClient) -> None:
    response = await api_client.get("/v1/students/1/", params={"token": "something"})
    assert response.status == HTTPStatus.FORBIDDEN


async def test_invalid_token_check_response(
    api_client: TestClient,
    forbidden_resp: dict[str, int | str],
) -> None:
    response = await api_client.get("/v1/students/1/", params={"token": "something"})
    assert await response.json() == forbidden_resp


async def test_student_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.get("/v1/students/0/", params={"token": token})
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Student not found",
    }


async def test_successful_read(
    api_client: TestClient,
    token: str,
    create_student: Callable,
) -> None:
    student = await create_student()
    response = await api_client.get(
        f"/v1/students/{student.id}/", params={"token": token}
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "created_at": student.created_at.isoformat(),
        "updated_at": student.updated_at.isoformat(),
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "vk_id": student.vk_id,
    }
