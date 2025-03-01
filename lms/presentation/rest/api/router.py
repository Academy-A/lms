from fastapi import APIRouter

from lms.presentation.rest.api.v1.router import router as v1_router

api_router = APIRouter()
api_router.include_router(v1_router)
