from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from lms.db.uow import UnitOfWork
from lms.rest.api.deps import UnitOfWorkMarker
from lms.rest.api.v1.schemas import MonitoringSchema

router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


async def check_db(uow: UnitOfWork) -> bool:
    try:
        await uow._session.execute(text("select 1"))
        return True
    except SQLAlchemyError:
        return False


@router.get("/ping")
async def ping(
    response: Response, uow: UnitOfWork = Depends(UnitOfWorkMarker)
) -> MonitoringSchema:
    db_status = "ok"
    status_code = HTTPStatus.OK
    async with uow:
        if not await check_db(uow):
            db_status = "internal_error"
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    response.status_code = status_code
    return MonitoringSchema(db_status=db_status)
