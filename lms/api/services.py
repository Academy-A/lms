from collections.abc import MutableMapping
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyQuery
from jose import JWTError, jwt

from lms.api.deps import SettingsMarker
from lms.config import Settings

SECURITY_ALGORITHM = "HS256"


async def token_required(
    token: str = Depends(APIKeyQuery(name="token", auto_error=False)),
    settings: Settings = Depends(SettingsMarker),
) -> None:
    if settings.DEBUG:
        return
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not check_token(token=token, secret_key=settings.SECRET_KEY):
        raise HTTPException(status_code=403, detail="Token not recognized")


def check_token(token: str, secret_key: str) -> bool:
    try:
        jwt.decode(token=token, key=secret_key, algorithms=[SECURITY_ALGORITHM])
        return True
    except JWTError:
        return False


def generate_token(data: MutableMapping[str, Any], secret_key: str) -> str:
    return jwt.encode(data, key=secret_key, algorithm=SECURITY_ALGORITHM)