from fastapi import APIRouter, Depends, Query

from src.api.deps import DatabaseProviderMarker
from src.api.services import token_required
from src.api.v1.product.schemas import DistributionSchema, ProductPageSchema
from src.api.v1.schemas import StatusResponseSchema
from src.db.provider import DatabaseProvider
from src.tasks.config import celery

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(token_required)],
)


@router.get("/")
async def read_products(
    page: int = Query(gt=0, default=1),
    page_size: int = Query(gt=0, le=100, default=20),
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> ProductPageSchema:
    pagination = await provider.product.paginate(
        page=page,
        page_size=page_size,
    )
    return ProductPageSchema.from_pagination(pagination=pagination)


@router.post("/{product_id}/distribute")
async def create_distribution(
    product_id: int,
    distribution_data: DistributionSchema,
    provider: DatabaseProvider = Depends(DatabaseProviderMarker),
) -> StatusResponseSchema:
    await provider.product.read_by_id(product_id=product_id)
    celery.send_task(
        "make_distribution_task",
        kwargs={
            "homework_id": distribution_data.homework_id,
            "product_id": product_id,
            "teacher_types": distribution_data.teacher_types,
        },
    )
    return StatusResponseSchema(
        ok=True,
        status_code=201,
        message="The distribution task has been created",
    )