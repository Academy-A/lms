from loguru import logger
from sqlalchemy.orm import Session

from src.config import Settings
from src.controllers.homework_notification.subscription import SubscriptionNotification
from src.db.factory import create_engine, create_session_factory
from src.db.models import Setting, Subject


def get_settings(session: Session, key: str, default: str | None = None) -> str:
    setting = session.query(Setting).filter_by(key=key).first()
    if setting is None and default is None:
        raise KeyError(f"{key} not in table Setting")
    return str(getattr(setting, "value", default))


def main() -> None:
    settings = Settings()
    engine = create_engine(
        connection_uri=settings.build_db_connection_uri(driver="psycopg2")
    )
    SessionLocal = create_session_factory(engine=engine)
    with SessionLocal() as session:
        notify(session=session)
    engine.dispose()


def notify(session: Session) -> None:
    subjects = session.query(Subject).all()
    for subject in subjects:
        notification = SubscriptionNotification(
            session=session,
            subject_id=subject.id,
            subject_eng_name=subject.eng_name,
        )
        try:
            notification.init()
            notification.notify()
        except Exception:
            session.rollback()
            logger.exception("Occurred error:")


if __name__ == "__main__":
    main()
