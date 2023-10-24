from fastapi import APIRouter, Depends, Query

from lms.api.deps import UnitOfWorkMarker
from lms.api.services import token_required
from lms.api.v1.product.schemas import DistributionTaskSchema, ProductPageSchema
from lms.api.v1.schemas import StatusResponseSchema
from lms.db.uow import UnitOfWork
from lms.tasks.config import celery

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(token_required)],
)


@router.get("/")
async def read_products(
    page: int = Query(gt=0, default=1),
    page_size: int = Query(gt=0, le=100, default=20),
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> ProductPageSchema:
    async with uow:
        pagination = await uow.product.paginate(
            page=page,
            page_size=page_size,
        )
    return ProductPageSchema.from_pagination(pagination=pagination)


@router.post("/distribute/")
async def create_distribution(
    distribution_data: DistributionTaskSchema,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> StatusResponseSchema:
    await uow.product.read_by_id(product_id=distribution_data.product_id)
    celery.send_task(
        "make_distribution_task",
        kwargs={
            "distribution_data_str": distribution_data.model_dump_json(),
        },
    )
    return StatusResponseSchema(
        ok=True,
        status_code=201,
        message="The distribution task has been created",
    )
