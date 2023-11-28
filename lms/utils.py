from hashlib import sha256

from sqlalchemy.orm import Session

from lms.db.models import Setting


def get_setting(session: Session, key: str, default: str | None = None) -> str:
    setting = session.query(Setting).filter_by(key=key).first()
    if setting is None and default is None:
        raise KeyError(f"{key} not in table Setting")
    return str(getattr(setting, "value", default))


def encode_password(password: str, secret_key: str) -> str:
    passworded = password + secret_key
    hashed = sha256(passworded.encode())
    return hashed.hexdigest()


def check_password(password: str, secret_key: str, hashed_password: str) -> bool:
    return encode_password(password=password, secret_key=secret_key) == hashed_password
