from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView


class HomeView(CustomView):
    def is_accessible(self, request: Request) -> bool:
        return super().is_accessible(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        print(self.template_path)
        return templates.TemplateResponse(
            self.template_path, {"request": request, "some-info": "Very important"}
        )
