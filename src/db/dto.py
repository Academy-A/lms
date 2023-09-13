from dataclasses import dataclass, field
import math
from typing import Any, Sequence


@dataclass
class PaginationDTO:
    items: Sequence[Any]
    page: int
    page_size: int
    total: int
    pages: int = field(init=False)

    def __post_init__(self) -> None:
        self.pages = int(math.ceil(self.total / self.page_size)) or 1
