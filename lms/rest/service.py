import logging
from collections.abc import Callable

from aiomisc.service.uvicorn import UvicornApplication, UvicornService
from fastapi import BackgroundTasks, FastAPI, HTTPException
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


class REST(UvicornService):
    __required__ = (
        "debug",
        "project_name",
        "project_description",
        "project_version",
        "secret_key",
    )

    __dependencies__ = (
        "autopilot",
        "soho",
        "telegram",
        "session_factory",
        "get_distributor",
    )

    session_factory: async_sessionmaker[AsyncSession]
    autopilot: Autopilot
    soho: Soho
    telegram: Telegram
    get_distributor: Callable

    debug: bool
    project_name: str
    project_description: str
    project_version: str

    secret_key: str

    async def create_application(self) -> UvicornApplication:
        app = FastAPI(
            debug=self.debug,
            title=self.project_name,
            description=self.project_description,
            version=self.project_version,
        )
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        app.include_router(api_router)
        app.exception_handler(HTTPException)(http_exception_handler)
        app.exception_handler(RequestValidationError)(requset_validation_handler)
        app.exception_handler(LMSError)(lms_exception_handler)

        def get_enroller(background_tasks: BackgroundTasks) -> Enroller:
            return Enroller(
                uow=UnitOfWork(self.session_factory),
                autopilot=self.autopilot,
                telegram=self.telegram,
                background_tasks=background_tasks,
            )

        app.dependency_overrides.update(
            {
                UnitOfWorkMarker: lambda: UnitOfWork(self.session_factory),
                SecretKeyMarker: lambda: self.secret_key,
                DebugMarker: lambda: self.debug,
                AutopilotMarker: lambda: self.autopilot,
                SohoMarker: lambda: self.soho,
                TelegramMarker: lambda: self.telegram,
                EnrollerMarker: get_enroller,
                DistributorMarker: self.get_distributor,
            }
        )
        configure_admin(
            app=app,
            session_factory=self.session_factory,
            title=self.project_name,
            secret_key=self.secret_key,
            debug=self.debug,
        )
        log.info("REST service app configured")
        return app
