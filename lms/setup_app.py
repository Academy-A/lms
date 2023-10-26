import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.cors import CORSMiddleware

from lms.admin.setup_admin import build_admin
from lms.api.deps import (
    DatabaseEngineMarker,
    DatabaseSessionMarker,
    SettingsMarker,
    UnitOfWorkMarker,
)
from lms.api.router import api_router
from lms.api.v1.handler import (
    http_exception_handler,
    lms_exception_handler,
    requset_validation_handler,
)
from lms.config import Settings
from lms.db.factory import create_async_engine, create_async_session_factory
from lms.db.uow import UnitOfWork
from lms.exceptions.base import LMSError

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield

    engine: AsyncEngine = app.dependency_overrides[DatabaseEngineMarker]()
    await engine.dispose()


def get_application(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
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

    engine = create_async_engine(
        connection_uri=settings.build_db_connection_uri(), pool_pre_ping=True
    )
    session_factory = create_async_session_factory(engine=engine)
    uow = UnitOfWork(sessionmaker=session_factory)
    app.dependency_overrides.update(
        {
            SettingsMarker: lambda: settings,
            DatabaseEngineMarker: lambda: engine,
            DatabaseSessionMarker: lambda: session_factory,
            UnitOfWorkMarker: lambda: uow,
        },
    )
    build_admin(app=app, settings=settings, engine=engine)
    log.info("App configured")
    return app
