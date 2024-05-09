from http import HTTPStatus

from aiohttp.test_utils import TestClient


def api_url(product_id: int) -> str:
    return f"/v1/products/{product_id}/"


async def test_unauthorized_user_status(api_client: TestClient) -> None:
    response = await api_client.get(api_url(1))
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_user_format(api_client: TestClient) -> None:
    response = await api_client.get(api_url(1))
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token_status(api_client: TestClient) -> None:
    response = await api_client.get(api_url(1), params={"token": "something"})
    assert response.status == HTTPStatus.FORBIDDEN


async def test_invalid_token_format(api_client: TestClient) -> None:
    response = await api_client.get(api_url(1), params={"token": "something"})
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_product_not_found_status(api_client: TestClient, token: str) -> None:
    response = await api_client.get(api_url(0), params={"token": token})
    assert response.status == HTTPStatus.NOT_FOUND


async def test_product_not_found_format(api_client: TestClient, token: str) -> None:
    response = await api_client.get(api_url(0), params={"token": token})
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Product not found",
    }


async def test_success_status(
    api_client: TestClient,
    token: str,
    create_product,
):
    product = await create_product()
    response = await api_client.get(
        api_url(product_id=product.id),
        params={"token": token},
    )
    assert response.status == HTTPStatus.OK


async def test_success_format(
    api_client: TestClient,
    token: str,
    create_product,
) -> None:
    product = await create_product()
    response = await api_client.get(
        api_url(product_id=product.id),
        params={"token": token},
    )
    assert await response.json() == {
        "id": product.id,
        "product_group_id": product.product_group.id,
        "subject_id": product.subject_id,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat(),
        "name": product.name,
        "start_date": product.start_date.isoformat(),
        "end_date": product.end_date.isoformat(),
    }
