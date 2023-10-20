from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.v1.schemas import StatusResponseSchema
from src.exceptions import (
    EntityNotFoundError,
    LMSError,
    OfferNotFoundError,
    SohoNotFoundError,
    StudentAlreadyEnrolledError,
    StudentNotFoundError,
    StudentProductHasNotTeacherError,
    StudentVKIDAlreadyUsedError,
)
from src.exceptions.product import ProductNotFoundError
from src.exceptions.student import StudentProductNotFoundError


async def requset_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    for error in errors:
        if "url" in error:
            del error["url"]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": errors}),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return exception_json_response(status_code=exc.status_code, detail=exc.detail)


async def lms_exception_handler(request: Request, exc: LMSError) -> JSONResponse:
    if isinstance(exc, SohoNotFoundError):
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND, detail="Soho not found"
        )

    if isinstance(exc, StudentNotFoundError):
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    if isinstance(exc, StudentAlreadyEnrolledError):
        return exception_json_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled on product",
        )

    if isinstance(exc, StudentVKIDAlreadyUsedError):
        return exception_json_response(
            status_code=status.HTTP_409_CONFLICT, detail="VK ID already in database"
        )

    if isinstance(exc, OfferNotFoundError):
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer {exc.offer_id} not found",
        )

    if isinstance(exc, StudentProductHasNotTeacherError):
        return exception_json_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student has not mentor or motivator on this product",
        )

    if isinstance(exc, ProductNotFoundError):
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if isinstance(exc, StudentProductNotFoundError):
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="StudentProduct not found",
        )

    if isinstance(exc, EntityNotFoundError):
        logger.exception("Not concrete entity not found error")
        return exception_json_response(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found"
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
