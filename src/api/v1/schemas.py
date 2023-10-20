from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import BaseModel

from src.dto import PaginationData


class MonitoringSchema(BaseModel):
    status: Literal["ok"]


class StatusResponseSchema(BaseModel):
    ok: bool
    status_code: int
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
