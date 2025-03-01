from enum import StrEnum
from typing import Any

from sqladmin import ModelView
from sqlalchemy.orm import joinedload
from starlette.requests import Request


class AdminCategories(StrEnum):
    DASHBOARDS = "Dashboards"
    MODELS = "Models"


class BaseModelView(ModelView):
    can_delete = False
    list_template = "./custom_list.html"

    async def get_model_objects(
        self,
        request: Request,
        limit: int | None = 0,
    ) -> list[Any]:
        stmt = self.list_query(request)

        search = request.query_params.get("search", None)
        if search:
            stmt = self.search_query(stmt=stmt, term=search)

        limit = None if limit == 0 else limit
        if limit:
            stmt = stmt.limit(limit)

        for relation in self._list_relations:
            stmt = stmt.options(joinedload(relation))

        return await self._run_query(stmt)
