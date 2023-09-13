from fastapi import APIRouter

from src.api.v1.auth.router import router as auth_router
from src.api.v1.monitoring import router as monitoring_router
from src.api.v1.student.router import router as student_router
from src.api.v1.product.router import router as product_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(monitoring_router)
router.include_router(student_router)
router.include_router(product_router)
