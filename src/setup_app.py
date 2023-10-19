import logging

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.api.deps import (
    DatabaseEngineMarker,
    DatabaseProviderMarker,
    DatabaseSessionMarker,
    SettingsMarker,
)
from src.api.router import api_router
from src.api.v1.handler import (
    http_exception_handler,
    lms_exception_handler,
    requset_validation_handler,
)
from src.config import Settings
from src.db.factory import (
    create_async_engine,
    create_async_session_factory,
    create_provider,
)
from src.exceptions.base import LMSError

logging.root.setLevel(level=logging.INFO)


def get_application(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
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

    app.dependency_overrides.update(
        {
            SettingsMarker: lambda: settings,
            DatabaseEngineMarker: lambda: engine,
            DatabaseSessionMarker: lambda: session_factory,
            DatabaseProviderMarker: create_provider(session_factory=session_factory),
        },
    )
    logger.info("App configured")
    return app
