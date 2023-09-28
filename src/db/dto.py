import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PaginationData:
    items: Sequence[Any]
    page: int
    page_size: int
    total: int
    pages: int = field(init=False)

    def __post_init__(self) -> None:
        self.pages = int(math.ceil(self.total / self.page_size)) or 1
