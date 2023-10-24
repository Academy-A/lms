from sqlalchemy.orm import Session

from lms.db.models import Setting


def get_setting(session: Session, key: str, default: str | None = None) -> str:
    setting = session.query(Setting).filter_by(key=key).first()
    if setting is None and default is None:
        raise KeyError(f"{key} not in table Setting")
    return str(getattr(setting, "value", default))
