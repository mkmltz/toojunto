from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text

from . import models  # noqa: F401
from .auth.router import router as auth_router
from .config import Settings, settings
from .db import engine
from .groups.router import router as groups_router
from .invites.router import router as invites_router


def create_app(app_settings: Settings = settings) -> FastAPI:
    application = FastAPI(
        title="TooJunto API",
        version="0.1.0",
        docs_url=app_settings.docs_url,
        redoc_url=app_settings.redoc_url,
        openapi_url=app_settings.openapi_url,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=app_settings.allowed_hosts_list,
    )
    application.include_router(auth_router)
    application.include_router(groups_router)
    application.include_router(invites_router)

    @application.get("/health")
    def health():
        return {"status": "ok", "service": "toojunto-api", "version": "0.1.0"}

    @application.get("/health/db")
    def health_db():
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}

    return application


app = create_app()
