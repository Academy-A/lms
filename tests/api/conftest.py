from http import HTTPStatus

import pytest


@pytest.fixture
def unauthorized_resp() -> dict[str, int | str]:
    return {
        "ok": False,
        "status_code": HTTPStatus.UNAUTHORIZED,
        "message": "Unauthorized",
    }


@pytest.fixture
def forbidden_resp() -> dict[str, int | str]:
    return {
        "ok": False,
        "status_code": HTTPStatus.FORBIDDEN,
        "message": "Token not recognized",
    }
