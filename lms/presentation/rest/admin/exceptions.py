from collections.abc import Sequence
from typing import Any

from starlette.exceptions import HTTPException


class ExtendedHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        headers: dict | None = None,
        errors: Sequence[Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        if errors is None:
            errors = tuple()
        self._errors = errors

    def errors(self) -> Sequence[Any]:
        return self._errors
