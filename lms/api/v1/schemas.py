from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import BaseModel, PositiveInt

from lms.dto import PaginationData


class MonitoringSchema(BaseModel):
    db_status: Literal["ok", "internal_error"]


class StatusResponseSchema(BaseModel):
    ok: bool
    status_code: PositiveInt
    message: str


class MetaPageSchema(BaseModel):
    page: int
    pages: int
    total: int
    page_size: int


class PageSchema(BaseModel):
    meta: MetaPageSchema
    items: list[Any]

    @classmethod
    def from_pagination(cls, pagination: PaginationData) -> Self:
        return cls(
            meta=MetaPageSchema(
                page=pagination.page,
                pages=pagination.pages,
                total=pagination.total,
                page_size=pagination.page_size,
            ),
            items=pagination.items,
        )
