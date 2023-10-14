from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Flow, FlowProduct
from src.db.repositories.base import Repository


class FlowRepository(Repository[Flow]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Flow, session=session)

    async def get_by_soho_id(self, soho_flow_id: int) -> Flow | None:
        query = (
            select(Flow)
            .join(FlowProduct, Flow.id == FlowProduct.flow_id)
            .where(FlowProduct.soho_id == soho_flow_id)
        )
        return (await self._session.scalars(query)).first()
