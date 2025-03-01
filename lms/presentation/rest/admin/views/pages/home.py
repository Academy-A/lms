from http import HTTPMethod

from sqladmin import BaseView, expose
from starlette.requests import Request
from starlette.responses import Response


class HomePageView(BaseView):
    name = "Home"
    icon = "fa fa-home"

    @expose("/", methods=[HTTPMethod.GET])
    async def home(self, request: Request) -> Response:
        raise NotImplementedError
