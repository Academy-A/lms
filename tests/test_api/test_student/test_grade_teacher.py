from http import HTTPStatus
from typing import Any

import pytest
from aiohttp.test_utils import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.plugins.factories import (
    OfferFactory,
    ProductFactory,
    SohoAccountFactory,
    StudentProductFactory,
    TeacherProductFactory,
)


async def test_unauthorized_user_check_status(api_client: TestClient) -> None:
    response = await api_client.post("/v1/students/soho/1/grade-teacher/")
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_user_check_response(
    api_client: TestClient,
    unauthorized_resp: dict[str, int | str],
) -> None:
    response = await api_client.post("/v1/students/soho/1/grade-teacher/")
    assert await response.json() == unauthorized_resp


async def test_invalid_token_check_status(api_client: TestClient) -> None:
    response = await api_client.post(
        "/v1/students/soho/1/grade-teacher/", params={"token": "something"}
    )
    assert response.status == HTTPStatus.FORBIDDEN


async def test_invalid_token_check_response(
    api_client: TestClient,
    forbidden_resp: dict[str, int | str],
) -> None:
    response = await api_client.post(
        "/v1/students/soho/1/grade-teacher/", params={"token": "something"}
    )
    assert await response.json() == forbidden_resp


@pytest.mark.parametrize(
    ("json_data", "answer"),
    (
        pytest.param(
            None,
            {
                "detail": [
                    {
                        "input": None,
                        "loc": ["body"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ]
            },
            id="check missing body",
        ),
        pytest.param(
            {},
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": ["body", "grade"],
                        "msg": "Field required",
                        "input": {},
                    },
                    {
                        "type": "missing",
                        "loc": ["body", "product_id"],
                        "msg": "Field required",
                        "input": {},
                    },
                ]
            },
            id="check grade and product id missing",
        ),
        pytest.param(
            {
                "product_id": "rus",
                "grade": "excellent",
            },
            {
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": ["body", "grade"],
                        "msg": (
                            "Input should be a valid integer, unable to "
                            "parse string as an integer"
                        ),
                        "input": "excellent",
                    },
                    {
                        "type": "int_parsing",
                        "loc": ["body", "product_id"],
                        "msg": (
                            "Input should be a valid integer, unable to "
                            "parse string as an integer"
                        ),
                        "input": "rus",
                    },
                ]
            },
            id="check type grade and product id",
        ),
        pytest.param(
            {"product_id": 10, "grade": 10},
            {
                "detail": [
                    {
                        "type": "less_than_equal",
                        "loc": ["body", "grade"],
                        "msg": "Input should be less than or equal to 5",
                        "input": 10,
                        "ctx": {"le": 5},
                    }
                ]
            },
            id="check value grade <= 5",
        ),
        pytest.param(
            {"product_id": 10, "grade": -1},
            {
                "detail": [
                    {
                        "type": "greater_than_equal",
                        "loc": ["body", "grade"],
                        "msg": "Input should be greater than or equal to 0",
                        "input": -1,
                        "ctx": {"ge": 0},
                    }
                ]
            },
            id="check value grade >= 0",
        ),
    ),
)
async def test_validate_data(
    api_client: TestClient,
    token: str,
    json_data: dict[str, Any] | None,
    answer: dict[str, Any],
) -> None:
    response = await api_client.post(
        "/v1/students/soho/1/grade-teacher/",
        params={"token": token},
        json=json_data,
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert await response.json() == answer


async def test_soho_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.post(
        "v1/students/soho/0/grade-teacher/",
        params={"token": token},
        json={
            "product_id": 65,
            "grade": 5,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "SohoAccount not found",
    }


async def test_product_not_found(api_client: TestClient, token: str) -> None:
    soho = await SohoAccountFactory.create_async()
    response = await api_client.post(
        f"v1/students/soho/{soho.id}/grade-teacher/",
        params={"token": token},
        json={
            "product_id": 65,
            "grade": 5,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Product not found",
    }


async def test_student_product_not_found(api_client: TestClient, token: str) -> None:
    soho = await SohoAccountFactory.create_async()
    product = await ProductFactory.create_async()
    response = await api_client.post(
        f"/v1/students/soho/{soho.id}/grade-teacher/",
        params={"token": token},
        json={
            "product_id": product.id,
            "grade": 5,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "StudentProduct not found",
    }


async def test_student_product_has_not_teacher_product(
    api_client: TestClient,
    token: str,
) -> None:
    student_product = await StudentProductFactory.create_async(
        teacher_product=None,
        teacher_product_id=None,
        teacher_type=None,
    )
    soho = await SohoAccountFactory.create_async(student=student_product.student)
    response = await api_client.post(
        f"/v1/students/soho/{soho.id}/grade-teacher/",
        params={"token": token},
        json={
            "product_id": student_product.product.id,
            "grade": 5,
        },
    )
    assert response.status == HTTPStatus.BAD_REQUEST
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.BAD_REQUEST,
        "message": "Student has not mentor or motivator on this product",
    }


async def test_successful(
    api_client: TestClient, token: str, session: AsyncSession
) -> None:
    teacher_product = await TeacherProductFactory.create_async(
        average_grade=5,
        grade_counter=2,
    )
    offer = await OfferFactory.create_async(product=teacher_product.product)
    student_product = await StudentProductFactory.create_async(
        teacher_product=teacher_product,
        product=teacher_product.product,
        offer=offer,
        teacher_grade=None,
        teacher_graded_at=None,
    )
    soho = await SohoAccountFactory.create_async(student=student_product.student)
    response = await api_client.post(
        f"/v1/students/soho/{soho.id}/grade-teacher/",
        params={"token": token},
        json={
            "product_id": student_product.product.id,
            "grade": 2,
        },
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Teacher was graded",
    }
    await session.refresh(teacher_product)
    assert teacher_product.grade_counter == 3
    assert teacher_product.average_grade == 4

    await session.refresh(student_product)
    assert student_product.teacher_grade == 2
    assert student_product.teacher_graded_at is not None
