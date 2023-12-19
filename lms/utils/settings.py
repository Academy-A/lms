from lms.db.uow import UnitOfWork


class SettingStorage:
    _uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get(self, key: str, default: str | None = None) -> str:
        value = await self._uow.setting.get(key)
        if value is None:
            if default is None:
                raise KeyError(f"Key {key} not found in SettingStorage")
            return default
        return value
