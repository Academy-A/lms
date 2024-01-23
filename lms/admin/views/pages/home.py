from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView


class HomeView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            self.template_path,
            {
                "request": request,
                "some-info": "Very important",
            },
        )
