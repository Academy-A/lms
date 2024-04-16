from http import HTTPStatus

from aiohttp.test_utils import TestClient


async def test_unauthorized_user(api_client: TestClient) -> None:
    response = await api_client.get("/v1/products/1/")
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(api_client: TestClient) -> None:
    response = await api_client.get("/v1/products/1/", params={"token": "something"})
    assert response.status == HTTPStatus.FORBIDDEN
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_subject_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.get("/v1/products/0/", params={"token": token})
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Product not found",
    }


async def test_succesful_status_ok(
    api_client: TestClient,
    token: str,
    create_product,
):
    product = await create_product()
    response = await api_client.get(
        f"/v1/products/{product.id}/",
        params={"token": token},
    )
    assert response.status == HTTPStatus.OK


async def test_successful_format_ok(
    api_client: TestClient,
    token: str,
    create_product,
) -> None:
    product = await create_product()
    response = await api_client.get(
        f"/v1/products/{product.id}/",
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
