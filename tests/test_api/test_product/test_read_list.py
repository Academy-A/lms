from datetime import date
from http import HTTPStatus

from httpx import AsyncClient

from tests.factories import ProductFactory


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.get("/v1/products/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/v1/products/", params={"token": "invalid-token"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_successful_empty_list(client: AsyncClient, token: str) -> None:
    response = await client.get("/v1/products/", params={"token": token})
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
    products = await ProductFactory.create_batch_async(
        size=5, start_date=date.today(), end_date=date.today()
    )
    response = await client.get("/v1/products/", params={"token": token})
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
                "id": p.id,
                "product_group_id": p.product_group.id,
                "subject_id": p.subject_id,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
                "name": p.name,
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(),
                "drive_folder_id": p.drive_folder_id,
                "check_spreadsheet_id": p.check_spreadsheet_id,
            }
            for p in sorted(products, key=lambda s: s.id)
        ],
    }
