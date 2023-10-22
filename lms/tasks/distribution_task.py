from loguru import logger
from sqlalchemy.orm import Session

from lms.controllers.homework_distribution.distribution import distribute_homeworks
from lms.tasks.base import DatabaseTask
from lms.tasks.config import celery


@celery.task(name="homework_distribution_task", bind=True, track_started=True)
def make_distribution_task(
    self: DatabaseTask,
    homework_id: int,
    product_id: int,
    teacher_types: list[str | None],
) -> None:
    logger.info(
        "Started task for homework_id={homework_id} product_id={product_id}",
        homework_id=homework_id,
        product_id=product_id,
    )
    with Session(self.engine) as session:
        distribute_homeworks(
            settings=self.settings,
            session=session,
            homework_id=homework_id,
            product_id=product_id,
            teacher_types=teacher_types,
        )
    logger.info("Task ended")
    return
