# from celery import Celery

# from lms.config import Settings
# from lms.tasks.base import DatabaseTask

# settings = Settings()

# celery = Celery(
#     __name__,
#     broker=settings.build_rabbitmq_connection_url(),
#     backend="db+" + settings.build_db_connection_uri(driver="psycopg2"),
#     task_cls=DatabaseTask,
#     result_extended=True,
#     imports=[
#         "lms.tasks.distribution_task",
#     ],
# )
