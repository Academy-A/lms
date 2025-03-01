from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.adapters.db.models import Flow as FlowDb
from lms.adapters.db.models import FlowProduct as FlowProductDb
from lms.adapters.db.repositories.base import Repository
from lms.generals.models.flow import Flow


class FlowRepository(Repository[FlowDb]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=FlowDb, session=session)

    async def get_by_soho_id(self, soho_flow_id: int) -> Flow | None:
        query = (
            select(FlowDb)
            .join(FlowProductDb, FlowDb.id == FlowProductDb.flow_id)
            .where(FlowProductDb.soho_id == soho_flow_id)
        )
        obj = (await self._session.scalars(query)).first()
        return Flow.model_validate(obj) if obj else None
