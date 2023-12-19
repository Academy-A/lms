from http import HTTPStatus

from aiohttp.test_utils import TestClient


async def test_ping_route(api_client: TestClient) -> None:
    response = await api_client.get("v1/monitoring/ping")
    assert response.status == HTTPStatus.OK
    assert await response.json() == {"db_status": "ok"}
