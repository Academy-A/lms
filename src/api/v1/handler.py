from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.v1.schemas import StatusResponseSchema
from src.exceptions import LMSError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return exception_json_response(status_code=exc.status_code, detail=exc.detail)


async def lms_exception_handler(request: Request, exc: LMSError) -> JSONResponse:
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
        ).dict(),
    )
