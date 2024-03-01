from http import HTTPStatus
from typing import Any

import pytest
from aiohttp.test_utils import TestClient
from yarl import URL

API_URL = URL("/v1/students/")


async def test_unauthorized_user_check_status(api_client: TestClient):
    response = await api_client.post(API_URL)
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_user_check_response(
    api_client: TestClient,
    unauthorized_resp: dict[str, int | str],
):
    response = await api_client.post(API_URL)
    assert await response.json() == unauthorized_resp


async def test_invalid_token_check_status(api_client: TestClient):
    response = await api_client.post(API_URL, params={"token": "something"})
    assert response.status == HTTPStatus.FORBIDDEN


async def test_invalid_token_check_response(
    api_client: TestClient,
    forbidden_resp: dict[str, int | str],
):
    response = await api_client.post(API_URL, params={"token": "something"})
    assert await response.json() == forbidden_resp


@pytest.mark.parametrize(
    "json_data",
    (
        None,
        {},
        {"student": {}, "offer_ids": ["a", "b", "c"]},
        {
            "student": {
                "raw_soho_flow_id": "test",
                "vk_id": 1,
                "soho_id": 1,
                "email": "test",
            },
            "offer_ids": [1],
        },
    ),
)
async def test_validate_data(
    api_client: TestClient,
    token: str,
    json_data: dict[str, Any] | None,
):
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json=json_data,
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
