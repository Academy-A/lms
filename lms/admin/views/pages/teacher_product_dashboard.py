from collections.abc import Sequence
from datetime import timedelta

from aiocache import cached
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from lms.admin.utils import template_cache_key_builder
from lms.db.repositories.product import ProductRepository
from lms.db.repositories.teacher_product import TeacherProductRepository
from lms.generals.enums import TeacherType
from lms.generals.models.teacher_dashboard import TeacherDashboardRow


def parse_teacher_dashboard_data(
    teacher_data: list[TeacherDashboardRow],
) -> dict[str, list[TeacherDashboardRow]]:
    data: dict[str, list[TeacherDashboardRow]] = {}
    for t in TeacherType:
        data[t] = list()
    for td in teacher_data:
        data[td.type].append(td)

    return data


class TeacherProductDashboardView(CustomView):
    CACHE_TTL = timedelta(minutes=10).total_seconds()
    _product_ids: Sequence[int]

    def __init__(
        self,
        label: str,
        product_ids: Sequence[int],
        icon: str | None = None,
        path: str = "/",
        template_path: str = "index.html",
        name: str | None = None,
        methods: list[str] | None = None,
        add_to_menu: bool = True,
    ):
        super().__init__(label, icon, path, template_path, name, methods, add_to_menu)
        self._product_ids = product_ids

    @cached(ttl=CACHE_TTL, key_builder=template_cache_key_builder)
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        tpr = TeacherProductRepository(request.state.session)
        pr = ProductRepository(request.state.session)
        dashboard = []

        for product_id in self._product_ids:
            raw_data = await tpr.get_dashboard_data(product_id=product_id)
            teacher_data = parse_teacher_dashboard_data(raw_data)
            product = await pr.read_by_id(product_id=product_id)
            dashboard.append({"product": product, "teachers": teacher_data})
        return templates.TemplateResponse(
            self.template_path,
            {
                "request": request,
                "dashboard": dashboard,
            },
        )
