import logging

from sqlalchemy.orm import Session

from lms.config import Settings
from lms.controllers.homework_notification.subscription import SubscriptionNotification
from lms.db.factory import create_engine, create_session_factory
from lms.db.models import Subject

log = logging.getLogger(__name__)


def main() -> None:
    log.info("subscription notify | start")
    settings = Settings()
    engine = create_engine(
        connection_uri=settings.build_db_connection_uri(driver="psycopg2")
    )
    SessionLocal = create_session_factory(engine=engine)
    with SessionLocal() as session:
        notify(session=session)
    engine.dispose()
    log.info("subscription notify | end")


def notify(session: Session) -> None:
    subjects = session.query(Subject).filter(Subject.id == 1).order_by(Subject.id).all()
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
            log.exception("Occurred error:")


if __name__ == "__main__":
    main()
