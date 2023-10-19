from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    ProductFactory,
    SohoFactory,
    StudentProductFactory,
    TeacherProductFactory,
)

pytestmark = [pytest.mark.asyncio]


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.post(f"v1/students/soho/1/grade-teacher")
    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "status_code": 401,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "v1/students/soho/1/grade-teacher", params={"token": "something"}
    )
    assert response.status_code == 403
    assert response.json() == {
        "ok": False,
        "status_code": 403,
        "message": "Token not recognized",
    }


@pytest.mark.parametrize(
    "json_data,answer",
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
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "excellent",
                    },
                    {
                        "type": "int_parsing",
                        "loc": ["body", "product_id"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
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
    json_data: dict[str, Any] | None,
    answer: dict[str, Any],
    client: AsyncClient,
    token: str,
) -> None:
    response = await client.post(
        "v1/students/soho/1/grade-teacher",
        params={"token": token},
        json=json_data,
    )
    assert response.status_code == 422
    assert response.json() == answer


async def test_soho_not_found(client: AsyncClient, token: str) -> None:
    response = await client.post(
        "v1/students/soho/0/grade-teacher",
        params={"token": token},
        json={
            "product_id": 65,
            "grade": 5,
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "status_code": 404,
        "message": "Soho not found",
    }


async def test_product_not_found(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    soho = await SohoFactory.create_async()
    response = await client.post(
        f"v1/students/soho/{soho.id}/grade-teacher",
        params={"token": token},
        json={
            "product_id": 65,
            "grade": 5,
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "status_code": 404,
        "message": "Product not found",
    }


async def test_student_product_not_found(client: AsyncClient, token: str) -> None:
    soho = await SohoFactory.create_async()
    product = await ProductFactory.create_async()
    response = await client.post(
        f"v1/students/soho/{soho.id}/grade-teacher",
        params={"token": token},
        json={
            "product_id": product.id,
            "grade": 5,
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "status_code": 404,
        "message": "StudentProduct not found",
    }


async def test_student_product_has_not_teacher_product(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    student_product = await StudentProductFactory.create_async(
        teacher_product=None,
        teacher_product_id=None,
        teacher_type=None,
    )
    soho = await SohoFactory.create_async(student=student_product.student)
    response = await client.post(
        f"v1/students/soho/{soho.id}/grade-teacher",
        params={"token": token},
        json={
            "product_id": student_product.product.id,
            "grade": 5,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "ok": False,
        "status_code": 400,
        "message": "Student has not mentor or motivator on this product",
    }


async def test_successful(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    teacher_product = await TeacherProductFactory.create_async(
        average_grade=5,
        grade_counter=2,
    )
    student_product = await StudentProductFactory.create_async(
        teacher_product=teacher_product,
        product=teacher_product.product,
    )
    soho = await SohoFactory.create_async(student=student_product.student)
    response = await client.post(
        f"v1/students/soho/{soho.id}/grade-teacher",
        params={"token": token},
        json={
            "product_id": student_product.product.id,
            "grade": 2,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "status_code": 200,
        "message": "Teacher was graded",
    }
    await session.refresh(teacher_product)
    assert teacher_product.grade_counter == 3
    assert teacher_product.average_grade == 4
