from datetime import timedelta
from typing import Any

from aiocache import cached
from sqladmin import BaseView, expose
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import Response

from lms.admin.utils import template_cache_key_builder
from lms.admin.views.base import AdminCategories
from lms.db.repositories.product import ProductRepository
from lms.db.repositories.teacher_product import TeacherProductRepository
from lms.generals.enums import TeacherType
from lms.generals.models.teacher_dashboard import TeacherDashboardRow


class TeacherProductDashboardView(BaseView):
    category = AdminCategories.DASHBOARDS
    name = "Teacher dashboard"
    session_factory: async_sessionmaker[AsyncSession]

    CACHE_TTL = timedelta(minutes=10).total_seconds()

    @expose("/dashboards/annual/", identity="annual")
    @cached(ttl=CACHE_TTL, key_builder=template_cache_key_builder)
    async def dashboard_annual(self, request: Request) -> Response:
        product_ids = [65, 66, 67, 68]
        dashboard = await self._load_dashboard_data(product_ids)
        return await self.templates.TemplateResponse(
            request=request,
            name="./teacher_product_dashboard.html",
            context={"dashboard": dashboard, "title": "Годовые курсы 2023/24"},
        )

    @expose("/dashboards/semiannual/", identity="semiannual")
    @cached(ttl=CACHE_TTL, key_builder=template_cache_key_builder)
    async def dashboard_semiannual(self, request: Request) -> Response:
        product_ids = [73, 74, 75, 76]
        dashboard = await self._load_dashboard_data(product_ids)
        return await self.templates.TemplateResponse(
            request=request,
            name="./teacher_product_dashboard.html",
            context={
                "dashboard": dashboard,
                "title": "Полугодовые курсы 2024",
            },
        )

    @expose("/dashboards/sotochka/", identity="sotochka")
    @cached(ttl=CACHE_TTL, key_builder=template_cache_key_builder)
    async def dashboard_sotochka(self, request: Request) -> Response:
        product_ids = [77, 78, 79, 80]
        dashboard = await self._load_dashboard_data(product_ids=product_ids)
        return await self.templates.TemplateResponse(
            request=request,
            name="./teacher_product_dashboard.html",
            context={"dashboard": dashboard, "title": "Ещё чуть-чуть и соточка"},
        )

    @expose("/dashboards/new-24-25/", identity="new_24_25")
    @cached(ttl=CACHE_TTL, key_builder=template_cache_key_builder)
    async def dashboard_summer_2024(self, request: Request) -> Response:
        product_ids = [81, 82, 83, 84, 85, 86]
        dashboard = await self._load_dashboard_data(product_ids=product_ids)
        return await self.templates.TemplateResponse(
            request=request,
            name="./teacher_product_dashboard.html",
            context={"dashboard": dashboard, "title": "Курсы 2024/25"},
        )

    async def _load_dashboard_data(
        self,
        product_ids: list[int],
    ) -> list[dict[str, Any]]:
        async with self.session_factory() as session:
            tpr = TeacherProductRepository(session)
            pr = ProductRepository(session)
            dashboard = []

            for product_id in product_ids:
                raw_data = await tpr.get_dashboard_data(product_id=product_id)
                teacher_data = parse_teacher_dashboard_data(raw_data)
                product = await pr.read_by_id(product_id=product_id)
                dashboard.append({"product": product, "teachers": teacher_data})

            return dashboard


def parse_teacher_dashboard_data(
    teacher_data: list[TeacherDashboardRow],
) -> dict[str, list[TeacherDashboardRow]]:
    data: dict[str, list[TeacherDashboardRow]] = {}
    for t in TeacherType:
        data[t] = list()
    for td in teacher_data:
        data[td.type].append(td)

    return data
