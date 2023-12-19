from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Setting
from lms.db.repositories.base import Repository


class SettingRepository(Repository[Setting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Setting, session=session)

    async def get(self, key: str) -> str | None:
        query = select(Setting).filter_by(key=key)
        setting = (await self._session.scalars(query)).first()
        return setting.value if setting else None
