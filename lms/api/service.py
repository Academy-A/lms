import logging

from aiomisc.service.uvicorn import UvicornApplication, UvicornService
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.cors import CORSMiddleware

from lms.admin.setup_admin import build_admin
from lms.api.deps import (
    DebugMarker,
    SecretKeyMarker,
    TelegramClientMarker,
    UnitOfWorkMarker,
)
from lms.api.router import api_router
from lms.api.v1.handler import (
    http_exception_handler,
    lms_exception_handler,
    requset_validation_handler,
)
from lms.clients.telegram import TelegramClient
from lms.db.uow import UnitOfWork
from lms.exceptions.base import LMSError

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
        "engine",
        "telegram_client",
        "uow",
    )

    engine: AsyncEngine
    telegram_client: TelegramClient
    uow: UnitOfWork

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

        app.dependency_overrides.update(
            {
                UnitOfWorkMarker: lambda: self.uow,
                SecretKeyMarker: lambda: self.secret_key,
                DebugMarker: lambda: self.debug,
                TelegramClientMarker: lambda: self.telegram_client,
            }
        )
        build_admin(
            app=app,
            engine=self.engine,
            project_name=self.project_name,
            secret_key=self.secret_key,
            debug=self.debug,
        )
        log.info("REST service app configured")
        return app
