from http import HTTPStatus

from httpx import AsyncClient

from tests.factories import SubjectFactory


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.get("/v1/subjects/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/v1/subjects/", params={"token": "invalid-token"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_successful_empty_list(client: AsyncClient, token: str) -> None:
    response = await client.get("/v1/subjects/", params={"token": token})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "meta": {
            "page": 1,
            "pages": 1,
            "total": 0,
            "page_size": 20,
        },
        "items": [],
    }


async def test_successful_order(client: AsyncClient, token: str) -> None:
    subjects = await SubjectFactory.create_batch_async(size=5)
    response = await client.get("/v1/subjects/", params={"token": token})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "meta": {
            "page": 1,
            "pages": 1,
            "total": 5,
            "page_size": 20,
        },
        "items": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat(timespec="seconds"),
                "updated_at": s.updated_at.isoformat(timespec="seconds"),
                "name": s.name,
                "eng_name": s.eng_name,
                "autopilot_url": s.autopilot_url,
                "group_vk_url": s.group_vk_url,
            }
            for s in sorted(subjects, key=lambda s: s.id)
        ],
    }
