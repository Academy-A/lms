from fastapi import Depends, HTTPException
from fastapi.security import APIKeyQuery
from jose import JWTError, jwt

from src.api.deps import SettingsMarker
from src.config import Settings


async def token_required(
    token: str = Depends(APIKeyQuery(name="token")),
    settings: Settings = Depends(SettingsMarker),
) -> None:
    if settings.DEBUG:
        return
    try:
        jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM],
        )
    except JWTError as e:
        raise HTTPException(status_code=403, detail="Token not recognized") from e
