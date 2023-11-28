from http import HTTPStatus

from httpx import AsyncClient


async def test_ping_route(client: AsyncClient) -> None:
    response = await client.get("v1/monitoring/ping")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
