from http import HTTPStatus

from aiohttp.test_utils import TestClient

from tests.plugins.factories import SubjectFactory


async def test_unauthorized_user(api_client: TestClient) -> None:
    response = await api_client.get("/v1/subjects/")
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(api_client: TestClient) -> None:
    response = await api_client.get("/v1/subjects/", params={"token": "invalid-token"})
    assert response.status == HTTPStatus.FORBIDDEN
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_successful_empty_list(api_client: TestClient, token: str) -> None:
    response = await api_client.get("/v1/subjects/", params={"token": token})
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "meta": {
            "page": 1,
            "pages": 1,
            "total": 0,
            "page_size": 20,
        },
        "items": [],
    }


async def test_successful_order(api_client: TestClient, token: str) -> None:
    subjects = await SubjectFactory.create_batch_async(size=5)
    response = await api_client.get("/v1/subjects/", params={"token": token})
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "meta": {
            "page": 1,
            "pages": 1,
            "total": 5,
            "page_size": 20,
        },
        "items": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
                "name": s.name,
                "eng_name": s.eng_name,
                "autopilot_url": s.autopilot_url,
                "group_vk_url": s.group_vk_url,
            }
            for s in sorted(subjects, key=lambda s: s.id)
        ],
    }
