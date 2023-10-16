import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import SohoFactory, StudentFactory

pytestmark = [pytest.mark.asyncio]


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.post("v1/students/soho/1/change-vk-id")
    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "status_code": 401,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "v1/students/soho/1/change-vk-id",
        params={"token": "something"},
    )
    assert response.status_code == 403
    assert response.json() == {
        "ok": False,
        "status_code": 403,
        "message": "Token not recognized",
    }


async def test_validate_data(
    client: AsyncClient, session: AsyncSession, token: str
) -> None:
    # check missing body
    response = await client.post(
        "v1/students/soho/1/change-vk-id",
        params={"token": token},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["body"],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.4/v/missing",
            }
        ]
    }

    # check vk id missing
    response = await client.post(
        "v1/students/soho/1/change-vk-id",
        params={"token": token},
        json={},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "vk_id"],
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2.4/v/missing",
            }
        ]
    }

    # check vk id type
    response = await client.post(
        f"v1/students/soho/1/change-vk-id",
        params={"token": token},
        json={"vk_id": "asdf"},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "int_parsing",
                "loc": ["body", "vk_id"],
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "asdf",
                "url": "https://errors.pydantic.dev/2.4/v/int_parsing",
            }
        ]
    }


async def test_soho_not_found(client: AsyncClient, token: str) -> None:
    response = await client.post(
        "v1/students/soho/0/change-vk-id", params={"token": token}, json={"vk_id": 1234}
    )
    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "status_code": 404,
        "message": "Soho not found",
    }


async def test_vk_id_already_used(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    student = await StudentFactory.create_async()
    soho = await SohoFactory.create_async()

    response = await client.post(
        f"v1/students/soho/{soho.id}/change-vk-id",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "ok": False,
        "status_code": 409,
        "message": "VK ID already in database",
    }


async def test_successful(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    soho = await SohoFactory.create_async()

    response = await client.post(
        f"v1/students/soho/{soho.id}/change-vk-id",
        params={"token": token},
        json={
            "vk_id": soho.student.vk_id + 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": soho.student.id,
        "first_name": soho.student.first_name,
        "last_name": soho.student.last_name,
        "vk_id": soho.student.vk_id + 1,
    }
