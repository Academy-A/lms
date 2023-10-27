from datetime import datetime
from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import TeacherAssignment
from lms.enums import TeacherType
from tests.factories import (
    OfferFactory,
    ProductFactory,
    StudentFactory,
    StudentProductFactory,
    TeacherAssignmentFactory,
    TeacherFactory,
    TeacherProductFactory,
)


async def test_unauthorized(client: AsyncClient) -> None:
    response = await client.post("/v1/students/change-teacher/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


async def test_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/students/change-teacher/", params={"token": "invalid-token"}
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
                        "type": "missing",
                        "loc": ["body"],
                        "msg": "Field required",
                        "input": None,
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
                        "loc": ["body", "product_id"],
                        "msg": "Field required",
                        "input": {},
                    },
                    {
                        "type": "missing",
                        "loc": ["body", "student_vk_id"],
                        "msg": "Field required",
                        "input": {},
                    },
                    {
                        "type": "missing",
                        "loc": ["body", "teacher_vk_id"],
                        "msg": "Field required",
                        "input": {},
                    },
                ]
            },
            id="check fields missing",
        ),
        pytest.param(
            {
                "student_vk_id": "student",
                "teacher_vk_id": "asdf",
                "product_id": -1,
            },
            {
                "detail": [
                    {
                        "type": "greater_than",
                        "loc": ["body", "product_id"],
                        "msg": "Input should be greater than 0",
                        "input": -1,
                        "ctx": {"gt": 0},
                    },
                    {
                        "type": "int_parsing",
                        "loc": ["body", "student_vk_id"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "student",
                    },
                    {
                        "type": "int_parsing",
                        "loc": ["body", "teacher_vk_id"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "asdf",
                    },
                ]
            },
            id="check fields type",
        ),
    ),
)
async def test_validate_data(
    json_data: dict[str, Any], answer: dict[str, Any], client: AsyncClient, token: str
) -> None:
    response = await client.post(
        "/v1/students/change-teacher/",
        params={"token": token},
        json=json_data,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == answer


async def test_student_not_found(client: AsyncClient, token: str) -> None:
    response = await client.post(
        "/v1/students/change-teacher/",
        params={"token": token},
        json={
            "student_vk_id": 1,
            "teacher_vk_id": 1,
            "product_id": 1,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Student not found",
    }


async def test_teacher_not_found(client: AsyncClient, token: str) -> None:
    student = await StudentFactory.create_async()
    response = await client.post(
        "/v1/students/change-teacher/",
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": 1,
            "product_id": 1,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Teacher not found",
    }


async def test_product_not_found(client: AsyncClient, token: str) -> None:
    student = await StudentFactory.create_async()
    teacher = await TeacherFactory.create_async()
    response = await client.post(
        "/v1/students/change-teacher/",
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": teacher.vk_id,
            "product_id": 1,
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
    teacher = await TeacherFactory.create_async()
    product = await ProductFactory.create_async()
    response = await client.post(
        "/v1/students/change-teacher/",
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": teacher.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "StudentProduct not found",
    }


async def test_teacher_product_not_found(client: AsyncClient, token: str) -> None:
    student = await StudentFactory.create_async()
    teacher = await TeacherFactory.create_async()
    product = await ProductFactory.create_async()
    offer = await OfferFactory.create_async(product=product)
    await StudentProductFactory.create_async(
        student=student,
        product=product,
        offer=offer,
        teacher_product=None,
        teacher_type=None,
    )
    response = await client.post(
        "/v1/students/change-teacher/",
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": teacher.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "TeacherProduct not found",
    }


async def test_same_teacher(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    student = await StudentFactory.create_async()
    teacher = await TeacherFactory.create_async()
    product = await ProductFactory.create_async()
    teacher_product = await TeacherProductFactory.create_async(
        teacher=teacher, product=product, type=TeacherType.CURATOR
    )
    offer = await OfferFactory.create_async(
        product=product, teacher_type=TeacherType.CURATOR
    )
    student_product = await StudentProductFactory.create_async(
        student=student,
        product=product,
        offer=offer,
        teacher_product=teacher_product,
        teacher_type=TeacherType.CURATOR,
    )
    ta = await TeacherAssignmentFactory.create_async(
        teacher_product=teacher_product,
        student_product=student_product,
        removed_at=None,
    )
    call_autopilot_mock = AsyncMock()
    with patch("lms.clients.autopilot.call_autopilot", call_autopilot_mock):
        response = await client.post(
            "/v1/students/change-teacher/",
            params={"token": token},
            json={
                "student_vk_id": student.vk_id,
                "teacher_vk_id": teacher.vk_id,
                "product_id": product.id,
            },
        )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Teacher was changed for student",
    }
    await session.refresh(ta)
    assert ta.removed_at is None

    call_autopilot_mock.assert_awaited_once()


@freeze_time("2023-10-27")
async def test_have_not_teacher_earlier(
    client: AsyncClient, token: str, session: AsyncSession
) -> None:
    student = await StudentFactory.create_async()
    teacher = await TeacherFactory.create_async()
    product = await ProductFactory.create_async()
    teacher_product = await TeacherProductFactory.create_async(
        teacher=teacher, product=product, type=TeacherType.CURATOR
    )
    offer = await OfferFactory.create_async(product=product, teacher_type=None)
    student_product = await StudentProductFactory.create_async(
        student=student,
        product=product,
        offer=offer,
        teacher_product=None,
        teacher_type=None,
    )
    call_autopilot_mock = AsyncMock()
    with patch("lms.clients.autopilot.call_autopilot", call_autopilot_mock):
        response = await client.post(
            "/v1/students/change-teacher/",
            params={"token": token},
            json={
                "student_vk_id": student.vk_id,
                "teacher_vk_id": teacher.vk_id,
                "product_id": product.id,
            },
        )
    call_autopilot_mock.assert_awaited_once()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Teacher was changed for student",
    }
    await session.refresh(student_product)
    assert student_product.teacher_product_id == teacher_product.id
    assert student_product.teacher_type == teacher_product.type

    ta = (
        await session.scalars(
            select(TeacherAssignment).filter_by(
                teacher_product_id=teacher_product.id,
                student_product_id=student_product.id,
            )
        )
    ).one()
    assert ta.teacher_product_id == teacher_product.id
    assert ta.student_product_id == student_product.id
    assert ta.removed_at is None
    assert ta.assignment_at == datetime.now()


@freeze_time("2023-10-27")
async def test_with_old_teacher_product(
    client: AsyncClient, token: str, session: str
) -> None:
    product = await ProductFactory.create_async()
    student = await StudentFactory.create_async()
    old_teacher = await TeacherFactory.create_async()
    old_teacher_product = await TeacherProductFactory.create_async(
        teacher=old_teacher,
        product=product,
        type=TeacherType.MENTOR,
    )
    teacher = await TeacherFactory.create_async()
    teacher_product = await TeacherProductFactory.create_async(
        teacher=teacher, product=product, type=TeacherType.CURATOR
    )
    offer = await OfferFactory.create_async(product=product, teacher_type=None)
    student_product = await StudentProductFactory.create_async(
        student=student,
        product=product,
        offer=offer,
        teacher_product=old_teacher_product,
        teacher_type=old_teacher_product.type,
    )
    call_autopilot_mock = AsyncMock()
    with patch("lms.clients.autopilot.call_autopilot", call_autopilot_mock):
        response = await client.post(
            "/v1/students/change-teacher/",
            params={"token": token},
            json={
                "student_vk_id": student.vk_id,
                "teacher_vk_id": teacher.vk_id,
                "product_id": product.id,
            },
        )
    call_autopilot_mock.assert_awaited_once()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Teacher was changed for student",
    }
    await session.refresh(student_product)
    assert student_product.teacher_product_id == teacher_product.id
    assert student_product.teacher_type == teacher_product.type

    ta = (
        await session.scalars(
            select(TeacherAssignment).filter_by(
                teacher_product_id=teacher_product.id,
                student_product_id=student_product.id,
            )
        )
    ).one()
    assert ta.teacher_product_id == teacher_product.id
    assert ta.student_product_id == student_product.id
    assert ta.removed_at is None
    assert ta.assignment_at == datetime.now()
