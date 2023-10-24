from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lms.db.models import Flow, FlowProduct
from lms.db.repositories.base import Repository
from lms.dto import FlowData


class FlowRepository(Repository[Flow]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Flow, session=session)

    async def get_by_soho_id(self, soho_flow_id: int) -> FlowData | None:
        query = (
            select(Flow)
            .join(FlowProduct, Flow.id == FlowProduct.flow_id)
            .where(FlowProduct.soho_id == soho_flow_id)
        )
        obj = (await self._session.scalars(query)).first()
        return FlowData.from_orm(obj) if obj else None
