from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView


class HomeView(CustomView):
    def is_accessible(self, request: Request) -> bool:
        print(request.session)
        return super().is_accessible(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            "home.html", {"request": request, "some-info": "Very important"}
        )
