from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class NameGen:
    base_name: str
    dt: datetime
    homework_ids: Sequence[int]

    @property
    def sheet_title(self) -> str:
        return f"{self._prefix} {self.dt:%d.%m.%Y %H:%M:%S}"

    @property
    def folder_title(self) -> str:
        return f"{self._prefix}_Проверенные работы"

    @property
    def _prefix(self) -> str:
        hw = "_".join(str(hw_id) for hw_id in self.homework_ids)
        return f"{self._week_title}_{self.base_name}_({hw})"

    @property
    def _week_title(self) -> str:
        begin_date = self.dt - timedelta(days=self.dt.weekday())
        end_date = self.dt + timedelta(days=6 - self.dt.isoweekday())
        return f"{begin_date.strftime('%d.%m')}-{end_date.strftime('%d.%m')}"
