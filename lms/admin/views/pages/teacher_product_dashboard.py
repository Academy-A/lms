from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from lms.db.repositories.product import ProductRepository
from lms.db.repositories.teacher_product import TeacherProductRepository
from lms.dto import TeacherDashboardData
from lms.enums import TeacherType

PRODUCT_IDS = [65, 66, 67, 68]


def parse_teacher_dashboard_data(
    teacher_data: list[TeacherDashboardData],
) -> dict[str, list[TeacherDashboardData]]:
    data: dict[str, list[TeacherDashboardData]] = {}
    for t in TeacherType:
        data[t] = list()
    for td in teacher_data:
        data[td.type].append(td)

    return data


class TeacherProductDashboardView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        tpr = TeacherProductRepository(request.state.session)
        pr = ProductRepository(request.state.session)
        dashboard = []

        for product_id in PRODUCT_IDS:
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
