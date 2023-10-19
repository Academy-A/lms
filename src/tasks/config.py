from celery import Celery

from src.config import Settings
from src.tasks.base import DatabaseTask

settings = Settings()

celery = Celery(
    __name__,
    broker=settings.build_rabbitmq_connection_url(),
    backend="db+" + settings.build_db_connection_uri(driver="psycopg2"),
    task_cls=DatabaseTask,
    result_extended=True,
    imports=[
        "src.tasks.distribution_task",
    ],
)
