from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Setting as SettingDb
from lms.db.repositories.base import Repository
from lms.generals.models.setting import Setting


class SettingRepository(Repository[SettingDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=SettingDb, session=session)

    async def get(self, key: str) -> str | None:
        query = select(SettingDb).filter_by(key=key)
        setting = (await self._session.scalars(query)).first()
        return setting.value if setting else None

    async def update(self, key: str, value: str) -> Setting:
        obj = await self._update(SettingDb.key == key, value=value)
        return Setting.model_validate(obj)
