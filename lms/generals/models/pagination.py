from typing import Generic, TypeVar

from pydantic import BaseModel

ItemType = TypeVar("ItemType", bound=BaseModel)


class MetaPageData(BaseModel):
    page: int
    pages: int
    total: int
    page_size: int


class Pagination(BaseModel, Generic[ItemType]):
    meta: MetaPageData
    items: list[ItemType]
