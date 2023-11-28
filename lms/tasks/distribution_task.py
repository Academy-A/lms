# import logging

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session

# from lms.api.v1.product.schemas import (
#     DistributionHomeworkSchema,
#     DistributionTaskSchema,
# )
# from lms.config import Settings
# from lms.controllers.homework_distribution.distribution import distribute_homeworks
# from lms.tasks.base import DatabaseTask
# from lms.tasks.config import celery

# log = logging.getLogger(__name__)


# @celery.task(name="homework_distribution_task", bind=True, track_started=True)
# def make_distribution_task(
#     self: DatabaseTask,
#     distribution_task_str: str,
# ) -> None:
#     distribution_task = DistributionTaskSchema.model_validate_json(
#         distribution_task_str
#     )
#     log.info(
#         "Started task for name=%s product_id=%s",
#         distribution_task.name,
#         distribution_task.product_id,
#     )
#     with Session(self.engine) as session:
#         distribute_homeworks(
#             settings=self.settings,
#             session=session,
#             distribution_task=distribution_task,
#         )
#     log.info("Task ended")
#     return


# def main() -> None:
#     settings = Settings()
#     engine = create_engine(
#         url=settings.build_db_connection_uri(driver="psycopg2"),
#     )
#     with Session(engine) as session:
#         distribute_homeworks(
#             settings=settings,
#             session=session,
#             distribution_task=DistributionTaskSchema(
#                 product_id=65,
#                 name="матем",
#                 homeworks=(
#                     DistributionHomeworkSchema(
#                         homework_id=46034,
#                         filters=tuple(),
#                     ),
#                     DistributionHomeworkSchema(
#                         homework_id=40342,
#                         filters=tuple(),
#                     ),
#                     DistributionHomeworkSchema(
#                         homework_id=33073,
#                         filters=tuple(),
#                     ),
#                 ),
#             ),
#         )


# if __name__ == "__main__":
#     main()
