from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.v1.schemas import StatusResponseSchema
from src.exceptions import LMSError, OfferNotFoundError, StudentAlreadyEnrolledError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return exception_json_response(status_code=exc.status_code, detail=exc.detail)


async def lms_exception_handler(request: Request, exc: LMSError) -> JSONResponse:
    if isinstance(exc, StudentAlreadyEnrolledError):
        return exception_json_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled on product",
        )

    if isinstance(exc, OfferNotFoundError):
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer {exc.offer_id} not found error",
        )

    logger.exception("Got unhandled error")
    return exception_json_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Got unhandled exception. See logs",
    )


def exception_json_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=StatusResponseSchema(
            ok=False,
            status_code=status_code,
            message=detail,
        ).model_dump(),
    )
