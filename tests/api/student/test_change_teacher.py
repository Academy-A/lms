from http import HTTPStatus
from typing import Any

import pytest
from aiohttp.test_utils import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yarl import URL

from lms.adapters.db.models import TeacherAssignment
from lms.generals.enums import TeacherType

API_URL = URL("/v1/students/change-teacher")


async def test_unauthorized_check_status(api_client: TestClient):
    response = await api_client.post(API_URL)
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_check_response(
    api_client: TestClient,
    unauthorized_resp: dict[str, int | str],
):
    response = await api_client.post(API_URL)
    assert await response.json() == unauthorized_resp


async def test_invalid_token_check_status(api_client: TestClient):
    response = await api_client.post(API_URL, params={"token": "invalid-token"})
    assert response.status == HTTPStatus.FORBIDDEN


async def test_invalid_token_check_response(
    api_client: TestClient,
    forbidden_resp: dict[str, int | str],
):
    response = await api_client.post(API_URL, params={"token": "invalid-token"})
    assert await response.json() == forbidden_resp


@pytest.mark.parametrize(
    ("json_data",),
    (
        pytest.param(None, id="check missing body"),
        pytest.param({}, id="check fields missing"),
        pytest.param(
            {
                "student_vk_id": "student",
                "teacher_vk_id": "asdf",
                "product_id": -1,
            },
            id="check fields type",
        ),
    ),
)
async def test_validate_data(
    json_data: dict[str, Any],
    api_client: TestClient,
    token: str,
):
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json=json_data,
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_student_not_found(api_client: TestClient, token: str):
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": 1,
            "teacher_vk_id": 1,
            "product_id": 1,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Student not found",
    }


async def test_teacher_not_found(
    api_client: TestClient,
    token: str,
    create_student,
):
    student = await create_student()
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": 1,
            "product_id": 1,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "Teacher not found",
    }


async def test_product_not_found(
    api_client: TestClient,
    token: str,
    create_student,
    create_teacher,
):
    student = await create_student()
    teacher = await create_teacher()
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": teacher.vk_id,
            "product_id": 1,
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
    create_teacher,
    create_product,
):
    product = await create_product()
    student = await create_student()
    teacher = await create_teacher()
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": teacher.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "StudentProduct not found",
    }


async def test_teacher_product_not_found(
    api_client: TestClient,
    token: str,
    create_offer,
    create_student,
    create_product,
    create_student_product,
    create_teacher,
):
    product = await create_product()
    student = await create_student()
    teacher = await create_teacher()
    offer = await create_offer(product=product)
    await create_student_product(
        student=student,
        product=product,
        offer=offer,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student.vk_id,
            "teacher_vk_id": teacher.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
    assert await response.json() == {
        "ok": False,
        "status_code": HTTPStatus.NOT_FOUND,
        "message": "TeacherProduct not found",
    }


async def test_same_teacher(
    api_client: TestClient,
    token: str,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
    create_teacher_assignment,
):
    product = await create_product()
    teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(
        product=product,
        teacher_type=TeacherType.CURATOR,
    )
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=teacher_product,
        teacher_type=TeacherType.CURATOR,
    )
    await create_teacher_assignment(
        teacher_product=teacher_product,
        student_product=student_product,
        removed_at=None,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student_product.student.vk_id,
            "teacher_vk_id": teacher_product.teacher.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Teacher was changed for student",
    }


async def test_have_not_teacher_earlier(
    api_client: TestClient,
    token: str,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
):
    product = await create_product()
    teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(
        product=product,
        teacher_type=TeacherType.CURATOR,
    )
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=teacher_product,
        teacher_type=TeacherType.CURATOR,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student_product.student.vk_id,
            "teacher_vk_id": teacher_product.teacher.vk_id,
            "product_id": product.id,
        },
    )
    assert response.status == HTTPStatus.OK


async def test_with_old_teacher_product(
    api_client: TestClient,
    token: str,
    session: AsyncSession,
    create_student_product,
    create_teacher_product,
    create_offer,
    create_product,
):
    product = await create_product()
    old_teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.MENTOR,
    )
    new_teacher_product = await create_teacher_product(
        product=product,
        type=TeacherType.CURATOR,
    )
    offer = await create_offer(product=product, teacher_type=None)
    student_product = await create_student_product(
        product=product,
        offer=offer,
        teacher_product=old_teacher_product,
        teacher_type=old_teacher_product.type,
    )
    response = await api_client.post(
        API_URL,
        params={"token": token},
        json={
            "student_vk_id": student_product.student.vk_id,
            "teacher_vk_id": new_teacher_product.teacher.vk_id,
            "product_id": product.id,
        },
    )

    assert response.status == HTTPStatus.OK
    assert await response.json() == {
        "ok": True,
        "status_code": HTTPStatus.OK,
        "message": "Teacher was changed for student",
    }
    await session.refresh(student_product)
    assert student_product.teacher_product_id == new_teacher_product.id
    assert student_product.teacher_type == new_teacher_product.type

    ta = (
        await session.scalars(
            select(TeacherAssignment).filter_by(
                teacher_product_id=new_teacher_product.id,
                student_product_id=student_product.id,
            )
        )
    ).one()
    assert ta.teacher_product_id == new_teacher_product.id
    assert ta.student_product_id == student_product.id
    assert ta.removed_at is None
    assert ta.assignment_at is not None
