from http import HTTPStatus
from typing import Any

import pytest
from aiohttp.test_utils import TestClient

from tests.plugins.factories import SohoAccountFactory, StudentFactory


async def test_unauthorized_user(api_client: TestClient) -> None:
    response = await api_client.post("/v1/students/soho/1/change-vk-id/")
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(api_client: TestClient) -> None:
    response = await api_client.post(
        "/v1/students/soho/1/change-vk-id/",
        params={"token": "something"},
    )
    assert response.status == HTTPStatus.FORBIDDEN
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


@pytest.mark.parametrize(
    ("json_data", "answer"),
    (
        pytest.param(
            None,
            {
                "detail": [
                    {
                        "input": None,
                        "loc": ["body"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ]
            },
            id="check missing body",
        ),
        pytest.param(
            {},
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": ["body", "vk_id"],
                        "msg": "Field required",
                        "input": {},
                    }
                ]
            },
            id="check vk id missing",
        ),
        pytest.param(
            {"vk_id": "asdf"},
            {
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": ["body", "vk_id"],
                        "msg": (
                            "Input should be a valid integer, unable to "
                            "parse string as an integer"
                        ),
                        "input": "asdf",
                    }
                ]
            },
            id="check vk id type",
        ),
    ),
)
async def test_validate_data(
    json_data: dict[str, Any] | None,
    answer: dict[str, Any],
    api_client: TestClient,
    token: str,
) -> None:
    response = await api_client.post(
        "/v1/students/soho/1/change-vk-id/",
        params={"token": token},
        json=json_data,
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert await response.json() == answer


async def test_soho_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.post(
        "/v1/students/soho/0/change-vk-id/",
        params={"token": token},
        json={"vk_id": 1234},
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "SohoAccount not found",
    }


async def test_vk_id_already_used(api_client: TestClient, token: str) -> None:
    student = await StudentFactory.create_async()
    soho = await SohoAccountFactory.create_async()

    response = await api_client.post(
        f"/v1/students/soho/{soho.id}/change-vk-id/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
        },
    )
    assert response.status == HTTPStatus.CONFLICT
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.CONFLICT,
        "message": "VK ID already in database",
    }


async def test_successful(api_client: TestClient, token: str) -> None:
    soho = await SohoAccountFactory.create_async()

    response = await api_client.post(
        f"/v1/students/soho/{soho.id}/change-vk-id/",
        params={"token": token},
        json={
            "vk_id": soho.student.vk_id + 1,
        },
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "id": soho.student.id,
        "first_name": soho.student.first_name,
        "last_name": soho.student.last_name,
        "vk_id": soho.student.vk_id + 1,
    }
