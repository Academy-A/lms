from fastapi import APIRouter

from src.api.v1.schemas import MonitoringSchema

router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


@router.get("/ping")
async def ping() -> MonitoringSchema:
    return MonitoringSchema(status="ok")
