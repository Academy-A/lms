from fastapi import APIRouter

from lms.rest.api.v1.monitoring import router as monitoring_router
from lms.rest.api.v1.product.router import router as product_router
from lms.rest.api.v1.student.router import router as student_router
from lms.rest.api.v1.subject.router import router as subject_router

router = APIRouter(prefix="/v1")
router.include_router(monitoring_router)
router.include_router(student_router)
router.include_router(product_router)
router.include_router(subject_router)
