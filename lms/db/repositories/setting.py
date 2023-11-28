from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Setting
from lms.db.repositories.base import Repository


class _None:
    pass


class SettingRepository(Repository[Setting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Setting, session=session)

    async def get(self, key: str, default: str | None | _None = _None()) -> str:
        query = select(Setting).filter_by(key=key)
        setting = (await self._session.scalars(query)).first()
        if setting is None and isinstance(default, _None):
            raise KeyError(f"{key} not in table Setting")
        return str(getattr(setting, "value", default))
