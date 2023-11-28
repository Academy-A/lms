from datetime import datetime
from http import HTTPStatus
from typing import Any

import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import TeacherAssignment
from lms.enums import TeacherType
from tests.factories import (
    ProductFactory,
    StudentFactory,
    StudentProductFactory,
    TeacherAssignmentFactory,
    TeacherProductFactory,
)

pytestmark = [pytest.mark.asyncio]


async def test_unauthorized_user(client: AsyncClient) -> None:
    response = await client.post("/v1/students/expulse/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/students/expulse/", params={"token": "invalid-token"}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


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
                        "loc": ["body", "vk_id"],
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
        ),
        pytest.param(
            {
                "product_id": "rus",
                "vk_id": "something",
            },
            {
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": ["body", "vk_id"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "something",
                    },
                    {
                        "type": "int_parsing",
                        "loc": ["body", "product_id"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "rus",
                    },
                ]
            },
        ),
    ),
)
async def test_validate_data(
    json_data: dict[str, Any], answer: dict[str, Any], client: AsyncClient, token: str
) -> None:
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json=json_data,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == answer


async def test_student_not_found(client: AsyncClient, token: str) -> None:
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={"vk_id": 1234, "product_id": 1},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Student not found",
    }


async def test_product_not_found(client: AsyncClient, token: str) -> None:
    student = await StudentFactory.create_async()
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": 1234,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Product not found",
    }


async def test_student_product_not_found(client: AsyncClient, token: str) -> None:
    student = await StudentFactory.create_async()
    product = await ProductFactory.create_async()
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": product.id,
        },
    )
    response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "StudentProduct not found",
    }


async def test_student_product_already_expulsed_error(
    client: AsyncClient,
    token: str,
) -> None:
    student = await StudentFactory.create_async()
    product = await ProductFactory.create_async()
    student_product = await StudentProductFactory.create_async(
        student=student,
        product=product,
        teacher_product=None,
        teacher_type=None,
        expulsion_at=datetime.now(),
    )
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.BAD_REQUEST,
        "message": "StudentProduct already expulsed",
    }


@freeze_time("2023-10-26")
async def test_successful_expulse_student_without_teacher(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    student = await StudentFactory.create_async()
    product = await ProductFactory.create_async()
    student_product = await StudentProductFactory.create_async(
        student=student,
        product=product,
        teacher_product=None,
        teacher_type=None,
        expulsion_at=None,
    )
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Student was expulsed from product",
    }

    await session.refresh(student_product)
    assert student_product.expulsion_at == datetime(2023, 10, 26)


@freeze_time("2023-10-26")
@pytest.mark.parametrize("teacher_type", (TeacherType.CURATOR, TeacherType.MENTOR))
async def test_successful_expulse_student_with_teacher(
    teacher_type: TeacherType, client: AsyncClient, token: str, session: AsyncSession
) -> None:
    product = await ProductFactory.create_async()
    teacher_product = await TeacherProductFactory.create_async(
        type=teacher_type,
        product=product,
    )
    student = await StudentFactory.create_async()
    student_product = await StudentProductFactory.create_async(
        student=student,
        teacher_product=teacher_product,
        teacher_type=teacher_type,
        product=product,
        expulsion_at=None,
    )
    teacher_assignment = await TeacherAssignmentFactory.create_async(
        student_product=student_product,
        teacher_product=teacher_product,
        removed_at=None,
    )
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Student was expulsed from product",
    }

    await session.refresh(student_product)
    assert student_product.expulsion_at == datetime(2023, 10, 26)
    assert student_product.teacher_product_id is None
    assert student_product.teacher_type is None

    await session.refresh(teacher_assignment)
    assert teacher_assignment.removed_at == datetime(2023, 10, 26)


@freeze_time("2023-10-26")
@pytest.mark.parametrize("teacher_type", (TeacherType.CURATOR, TeacherType.MENTOR))
async def test_successful_expulse_with_teacher_if_not_assignment(
    teacher_type: TeacherType, client: AsyncClient, token: str, session: AsyncSession
) -> None:
    product = await ProductFactory.create_async()
    teacher_product = await TeacherProductFactory.create_async(
        type=teacher_type,
        product=product,
    )
    student = await StudentFactory.create_async()
    student_product = await StudentProductFactory.create_async(
        student=student,
        teacher_product=teacher_product,
        teacher_type=teacher_type,
        product=product,
        expulsion_at=None,
    )
    response = await client.post(
        "/v1/students/expulse/",
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Student was expulsed from product",
    }

    await session.refresh(student_product)
    assert student_product.expulsion_at == datetime(2023, 10, 26)
    assert student_product.teacher_product_id is None
    assert student_product.teacher_type is None

    ta = (
        await session.scalars(
            select(TeacherAssignment).filter_by(
                student_product_id=student_product.id,
                teacher_product_id=teacher_product.id,
            )
        )
    ).first()
    assert ta is not None
    assert ta.removed_at == datetime(2023, 10, 26)
