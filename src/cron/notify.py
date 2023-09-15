from google_api_service_helper import GoogleDrive
from google_api_service_helper.utils import GoogleKeys
from loguru import logger
import orjson
from sqlalchemy.orm import Session

from src.config import Settings
from src.controllers.homework_notification.utils import get_cleaned_folder_ids
from src.db.factory import create_engine, create_session_factory
from src.db.models import Setting, Subject
from src.controllers.homework_notification.regular import RegularNotification


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
    autopilot_url = get_settings(session, RegularNotification.autopilot_url_key)
    google_keys = get_settings(session, "google_keys")
    gd = GoogleDrive(google_keys=GoogleKeys(**orjson.loads(google_keys)))

    for subject in subjects:
        try:
            regexp = get_settings(
                session, RegularNotification.regexp_setting + subject.eng_name
            )
            folder_ids = get_settings(
                session, RegularNotification.folder_ids_prefix + subject.eng_name
            )
            RegularNotification(
                session=session,
                subject_id=subject.id,
                autopilot_url=autopilot_url,
                regexp=regexp,
                root_folder_ids=get_cleaned_folder_ids(folder_ids),
                google_drive=gd,
            ).notify()
        except Exception:
            session.rollback()
            logger.exception("Occurred error:")


if __name__ == "__main__":
    main()
