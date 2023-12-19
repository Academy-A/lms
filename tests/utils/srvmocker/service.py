from collections import defaultdict
from collections.abc import Iterable
from contextlib import asynccontextmanager

from aiohttp import web
from aiohttp.test_utils import TestServer
from aiohttp.web_app import Application

from tests.utils.srvmocker.handlers import get_default_handler
from tests.utils.srvmocker.models import MockRoute, MockService


@asynccontextmanager
async def start_service(host: str, routes: Iterable[MockRoute]):
    app = Application()
    server = TestServer(app, host=host)
    for route in routes:
        app.router.add_route(
            method=route.method,
            path=route.path,
            handler=get_default_handler(route.handler_name),
        )
    await server.start_server()
    mock_service = MockService(
        history=list(),
        history_map=defaultdict(list),
        url=server.make_url(""),
        handlers=dict(),
    )
    context_key = web.AppKey("context", str)
    app[context_key] = mock_service
    try:
        yield mock_service
    finally:
        await server.close()
