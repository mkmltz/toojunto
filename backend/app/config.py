from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


DEVELOPMENT_DATABASE_URL = (
    "postgresql+psycopg://toojunto:toojunto_dev@localhost:5432/toojunto"
)
DEVELOPMENT_JWT_SECRET = "change-me-in-development"
DEVELOPMENT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
DEVELOPMENT_ALLOWED_HOSTS = "localhost,127.0.0.1,testserver"


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    app_env: Literal["development", "production"] = "development"
    database_url: str | None = None
    jwt_secret: str | None = None
    cors_origins: str = ""
    allowed_hosts: str = ""
    enable_api_docs: bool | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def apply_environment_policy(self) -> "Settings":
        if self.app_env == "development":
            self.database_url = self.database_url or DEVELOPMENT_DATABASE_URL
            self.jwt_secret = self.jwt_secret or DEVELOPMENT_JWT_SECRET
            self.cors_origins = self.cors_origins or DEVELOPMENT_CORS_ORIGINS
            self.allowed_hosts = self.allowed_hosts or DEVELOPMENT_ALLOWED_HOSTS
            if self.enable_api_docs is None:
                self.enable_api_docs = True
            return self

        if not self.database_url:
            raise ValueError("DATABASE_URL is required in production")
        try:
            database = make_url(self.database_url)
        except ArgumentError as error:
            raise ValueError("DATABASE_URL is invalid") from error
        if not database.drivername.startswith("postgresql") or not database.database:
            raise ValueError("DATABASE_URL must be a PostgreSQL URL in production")
        if database.host in {None, "localhost", "127.0.0.1"}:
            raise ValueError("DATABASE_URL cannot use a local host in production")
        if self.database_url == DEVELOPMENT_DATABASE_URL or database.password == "toojunto_dev":
            raise ValueError("DATABASE_URL cannot use development credentials in production")

        if not self.jwt_secret or self.jwt_secret == DEVELOPMENT_JWT_SECRET:
            raise ValueError("JWT_SECRET must be set to a secure value in production")
        if len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters in production")

        if not self.allowed_hosts_list:
            raise ValueError("ALLOWED_HOSTS is required in production")
        if "*" in self.allowed_hosts_list:
            raise ValueError("ALLOWED_HOSTS cannot contain '*' in production")

        if self.enable_api_docs is None:
            self.enable_api_docs = False
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return _split_csv(self.cors_origins)

    @property
    def allowed_hosts_list(self) -> list[str]:
        return _split_csv(self.allowed_hosts)

    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.enable_api_docs else None

    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.enable_api_docs else None

    @property
    def openapi_url(self) -> str | None:
        return "/openapi.json" if self.enable_api_docs else None


settings = Settings()
