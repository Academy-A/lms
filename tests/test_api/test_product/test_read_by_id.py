from datetime import date
from http import HTTPStatus

from aiohttp.test_utils import TestClient

from tests.factories import ProductFactory


async def test_unauthorized_user(http_client: TestClient) -> None:
    response = await http_client.get("/v1/products/1/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(http_client: TestClient) -> None:
    response = await client.get("/v1/products/1/", params={"token": "something"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_subject_not_found(http_client: TestClient, token: str) -> None:
    response = await client.get("/v1/products/0/", params={"token": token})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Product not found",
    }


async def test_successful_read(http_client: TestClient, token: str) -> None:
    product = await ProductFactory.create_async(
        start_date=date.today(), end_date=date.today()
    )
    response = await client.get(f"/v1/products/{product.id}/", params={"token": token})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": product.id,
        "product_group_id": product.product_group.id,
        "subject_id": product.subject_id,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat(),
        "name": product.name,
        "start_date": product.start_date.isoformat(),
        "end_date": product.end_date.isoformat(),
        "drive_folder_id": product.drive_folder_id,
        "check_spreadsheet_id": product.check_spreadsheet_id,
    }
