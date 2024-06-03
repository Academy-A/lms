import logging
from collections.abc import Callable

from aiomisc.service.uvicorn import UvicornApplication, UvicornService
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.middleware.cors import CORSMiddleware

from lms.admin.setup_admin import configure_admin
from lms.clients.autopilot import Autopilot
from lms.clients.soho import Soho
from lms.clients.telegram import Telegram
from lms.db.uow import UnitOfWork
from lms.exceptions.base import LMSError
from lms.logic.enroll_student import Enroller
from lms.rest.api.deps import (
    AutopilotMarker,
    DebugMarker,
    DistributorMarker,
    EnrollerMarker,
    SecretKeyMarker,
    SohoMarker,
    TelegramMarker,
    UnitOfWorkMarker,
)
from lms.rest.api.router import api_router
from lms.rest.api.v1.handler import (
    http_exception_handler,
    lms_exception_handler,
    requset_validation_handler,
)

log = logging.getLogger(__name__)

ExceptionHandlersType = tuple[tuple[type[Exception], Callable], ...]


class REST(UvicornService):
    __required__ = (
        "debug",
        "title",
        "description",
        "version",
        "secret_key",
    )
    __dependencies__ = (
        "autopilot",
        "soho",
        "telegram",
        "session_factory",
        "get_distributor",
        "enroller",
    )

    EXCEPTION_HANDLERS: ExceptionHandlersType = (
        (HTTPException, http_exception_handler),
        (RequestValidationError, requset_validation_handler),
        (LMSError, lms_exception_handler),
    )

    session_factory: async_sessionmaker[AsyncSession]
    autopilot: Autopilot
    soho: Soho
    telegram: Telegram
    get_distributor: Callable
    enroller: Enroller

    debug: bool
    title: str
    description: str
    version: str

    secret_key: str

    async def create_application(self) -> UvicornApplication:
        app = FastAPI(
            debug=self.debug,
            title=self.title,
            description=self.description,
            version=self.version,
            openapi_url="/docs/openapi.json",
            docs_url="/docs/swagger",
            redoc_url="/docs/redoc",
        )

        self._set_middlewares(app=app)
        self._set_routes(app=app)
        self._set_exceptions(app=app)
        self._set_dependency_overrides(app=app)

        configure_admin(
            app=app,
            session_factory=self.session_factory,
            title=self.title,
            secret_key=self.secret_key,
            debug=self.debug,
        )
        log.info("REST service app configured")
        return app

    def _set_middlewares(self, app: FastAPI) -> None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _set_routes(self, app: FastAPI) -> None:
        app.include_router(api_router)

    def _set_exceptions(self, app: FastAPI) -> None:
        for exception, handler in self.EXCEPTION_HANDLERS:
            app.add_exception_handler(exception, handler)

    def _set_dependency_overrides(self, app: FastAPI) -> None:
        app.dependency_overrides.update(
            {
                UnitOfWorkMarker: lambda: UnitOfWork(self.session_factory),
                SecretKeyMarker: lambda: self.secret_key,
                DebugMarker: lambda: self.debug,
                AutopilotMarker: lambda: self.autopilot,
                SohoMarker: lambda: self.soho,
                TelegramMarker: lambda: self.telegram,
                EnrollerMarker: lambda: self.enroller,
                DistributorMarker: self.get_distributor,
            }
        )
