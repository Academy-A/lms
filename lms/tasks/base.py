from celery import Task
from sqlalchemy import create_engine

from lms.config import Settings


class DatabaseTask(Task):
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings()
        self.engine = create_engine(
            url=self.settings.build_db_connection_uri(driver="psycopg2"),
        )
