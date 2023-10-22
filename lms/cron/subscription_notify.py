import logging

from loguru import logger
from sqlalchemy.orm import Session

from lms.config import Settings
from lms.controllers.homework_notification.subscription import SubscriptionNotification
from lms.db.factory import create_engine, create_session_factory
from lms.db.models import Setting, Subject

logging.basicConfig(level=logging.INFO)


def get_settings(session: Session, key: str, default: str | None = None) -> str:
    setting = session.query(Setting).filter_by(key=key).first()
    if setting is None and default is None:
        raise KeyError(f"{key} not in table Setting")
    return str(getattr(setting, "value", default))


def main() -> None:
    logger.info("subscription notify | start")
    settings = Settings()
    engine = create_engine(
        connection_uri=settings.build_db_connection_uri(driver="psycopg2")
    )
    SessionLocal = create_session_factory(engine=engine)
    with SessionLocal() as session:
        notify(session=session)
    engine.dispose()
    logger.info("subscription notify | end")


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
