from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, Query
from pydantic import PositiveInt

from lms.db.uow import UnitOfWork
from lms.generals.models.distribution import DistributionParams
from lms.generals.models.pagination import Pagination
from lms.generals.models.product import Product
from lms.logic.distribute_homeworks import Distributor
from lms.rest.api.auth import token_required
from lms.rest.api.deps import DistributorMarker, UnitOfWorkMarker
from lms.rest.api.v1.schemas import StatusResponseSchema

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
) -> Pagination[Product]:
    async with uow:
        pagination = await uow.product.paginate(
            page=page,
            page_size=page_size,
        )
    return pagination


@router.get(
    "/{product_id}/",
    response_model=Product,
    responses={
        HTTPStatus.OK: {"model": Product},
        HTTPStatus.FORBIDDEN: {"model": StatusResponseSchema},
        HTTPStatus.NOT_FOUND: {"model": StatusResponseSchema},
    },
)
async def read_product_by_id(
    product_id: PositiveInt,
    uow: UnitOfWork = Depends(UnitOfWorkMarker),
) -> Product:
    async with uow:
        product = await uow.product.read_by_id(product_id=product_id)
    return product


@router.post("/distribute/")
async def create_distribution(
    params: DistributionParams,
    distributor: Distributor = Depends(DistributorMarker),
) -> StatusResponseSchema:
    now = datetime.now()
    await distributor.make_distribution(params=params, created_at=now)
    return StatusResponseSchema(
        ok=True,
        status_code=HTTPStatus.CREATED,
        message="The distribution was created",
    )
