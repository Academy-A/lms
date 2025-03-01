from datetime import datetime
from http import HTTPStatus
from typing import Any

import pytest
from aiohttp.test_utils import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yarl import URL

from lms.adapters.db.models import TeacherAssignment
from lms.generals.enums import TeacherType

API_URL = URL("/v1/students/expulse/")


async def test_unauthorized_user_check_status(api_client: TestClient) -> None:
    response = await api_client.post(API_URL)
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_user_check_response(
    api_client: TestClient,
    unauthorized_resp: dict[str, int | str],
) -> None:
    response = await api_client.post(API_URL)
    assert await response.json() == unauthorized_resp


async def test_invalid_token_check_status(api_client: TestClient) -> None:
    response = await api_client.post(API_URL, params={"token": "invalid-token"})
    assert response.status == HTTPStatus.FORBIDDEN
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }


async def test_invalid_token_check_response(
    api_client: TestClient,
    forbidden_resp: dict[str, int | str],
) -> None:
    response = await api_client.post(API_URL, params={"token": "invalid-token"})
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
                        "msg": (
                            "Input should be a valid integer, unable to "
                            "parse string as an integer"
                        ),
                        "input": "something",
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
        ),
    ),
)
async def test_validate_data(
    api_client: TestClient,
    token: str,
    json_data: dict[str, Any],
    answer: dict[str, Any],
) -> None:
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json=json_data,
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert await response.json() == answer


async def test_student_not_found(api_client: TestClient, token: str) -> None:
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={"vk_id": 1234, "product_id": 1},
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Student not found",
    }


async def test_product_not_found(
    api_client: TestClient,
    token: str,
    create_student,
) -> None:
    student = await create_student()
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": 1234,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Product not found",
    }


async def test_student_product_not_found(
    api_client: TestClient,
    token: str,
    create_student,
    create_product,
) -> None:
    student = await create_student()
    product = await create_product()
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "vk_id": student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "StudentProduct not found",
    }


async def test_student_product_already_expulsed_error(
    api_client: TestClient,
    token: str,
    create_student_product,
) -> None:
    student_product = await create_student_product(expulsion_at=datetime.now())
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "vk_id": student_product.student.vk_id,
            "product_id": student_product.product.id,
        },
    )
    assert response.status == HTTPStatus.BAD_REQUEST
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.BAD_REQUEST,
        "message": "StudentProduct already expulsed",
    }


async def test_successful_expulse_student_without_teacher(
    api_client: TestClient,
    token: str,
    session: AsyncSession,
    create_student_product,
) -> None:
    student_product = await create_student_product(
        teacher_product=None,
        teacher_type=None,
        expulsion_at=None,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "vk_id": student_product.student.vk_id,
            "product_id": student_product.product.id,
        },
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Student was expulsed from product",
    }

    await session.refresh(student_product)
    assert student_product.expulsion_at is not None


@pytest.mark.parametrize("teacher_type", (TeacherType.CURATOR, TeacherType.MENTOR))
async def test_successful_expulse_student_with_teacher(
    api_client: TestClient,
    token: str,
    teacher_type: TeacherType,
    session: AsyncSession,
    create_product,
    create_student_product,
    create_teacher_assignment,
) -> None:
    product = await create_product()
    student_product = await create_student_product(
        teacher_product__product=product,
        teacher_product__type=teacher_type,
        offer__product=product,
        teacher_type=teacher_type,
        product=product,
        expulsion_at=None,
    )
    teacher_assignment = await create_teacher_assignment(
        student_product=student_product,
        teacher_product=student_product.teacher_product,
        removed_at=None,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "vk_id": student_product.student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Student was expulsed from product",
    }

    await session.refresh(student_product)
    assert student_product.expulsion_at is not None
    assert student_product.teacher_product_id is None
    assert student_product.teacher_type is None

    await session.refresh(teacher_assignment)
    assert teacher_assignment.removed_at is not None


@pytest.mark.parametrize("teacher_type", (TeacherType.CURATOR, TeacherType.MENTOR))
async def test_successful_expulse_with_teacher_if_not_assignment(
    api_client: TestClient,
    token: str,
    session: AsyncSession,
    teacher_type: TeacherType,
    create_product,
    create_student_product,
    create_teacher_product,
) -> None:
    product = await create_product()
    teacher_product = await create_teacher_product(
        product=product,
        type=teacher_type,
    )
    student_product = await create_student_product(
        teacher_product=teacher_product,
        teacher_type=teacher_type,
        product=product,
        expulsion_at=None,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "vk_id": student_product.student.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Student was expulsed from product",
    }

    await session.refresh(student_product)
    assert student_product.expulsion_at is not None
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
    assert ta.removed_at is not None
