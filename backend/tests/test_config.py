import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import (
    DEVELOPMENT_CORS_ORIGINS,
    DEVELOPMENT_DATABASE_URL,
    DEVELOPMENT_JWT_SECRET,
    Settings,
)
from app.main import create_app


PRODUCTION_DATABASE_URL = "postgresql+psycopg://app:strong-password@db:5432/toojunto"
PRODUCTION_JWT_SECRET = "a-production-secret-with-32-characters"


def production_settings(**overrides) -> Settings:
    values = {
        "app_env": "production",
        "database_url": PRODUCTION_DATABASE_URL,
        "jwt_secret": PRODUCTION_JWT_SECRET,
        "allowed_hosts": "toojunto.example",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_development_preserves_local_defaults():
    config = Settings(
        _env_file=None,
        app_env="development",
        database_url=None,
        jwt_secret=None,
        cors_origins="",
        allowed_hosts="",
        enable_api_docs=None,
    )

    assert config.database_url == DEVELOPMENT_DATABASE_URL
    assert config.jwt_secret == DEVELOPMENT_JWT_SECRET
    assert config.cors_origins == DEVELOPMENT_CORS_ORIGINS
    assert config.allowed_hosts_list == ["localhost", "127.0.0.1", "testserver"]
    assert config.enable_api_docs is True


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"database_url": None}, "DATABASE_URL is required"),
        ({"database_url": "not-a-url"}, "DATABASE_URL is invalid"),
        ({"database_url": DEVELOPMENT_DATABASE_URL}, "DATABASE_URL cannot use a local host"),
        ({"jwt_secret": None}, "JWT_SECRET must be set"),
        ({"jwt_secret": DEVELOPMENT_JWT_SECRET}, "JWT_SECRET must be set"),
        ({"jwt_secret": "too-short"}, "at least 32 characters"),
    ],
)
def test_production_rejects_missing_or_insecure_configuration(overrides, message):
    with pytest.raises(ValidationError, match=message):
        production_settings(**overrides)


def test_production_accepts_valid_configuration():
    config = production_settings()

    assert config.database_url == PRODUCTION_DATABASE_URL
    assert config.jwt_secret == PRODUCTION_JWT_SECRET
    assert config.enable_api_docs is False


def test_production_uses_explicit_cors_origins():
    config = production_settings(
        cors_origins="https://app.example, https://admin.example"
    )

    assert config.cors_origins_list == [
        "https://app.example",
        "https://admin.example",
    ]


def test_allowed_hosts_are_enforced():
    client = TestClient(create_app(production_settings()))

    assert client.get("/health", headers={"Host": "toojunto.example"}).status_code == 200
    assert client.get("/health", headers={"Host": "attacker.example"}).status_code == 400


def test_development_cors_allows_local_vite_origins():
    client = TestClient(
        create_app(
            Settings(
                _env_file=None,
                app_env="development",
                database_url=None,
                jwt_secret=None,
                cors_origins="",
                allowed_hosts="",
            )
        )
    )

    for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin


def test_production_cors_uses_only_explicit_origins():
    client = TestClient(
        create_app(production_settings(cors_origins="https://toojunto.example"))
    )
    headers = {
        "Host": "toojunto.example",
        "Origin": "https://toojunto.example",
        "Access-Control-Request-Method": "GET",
    }

    response = client.options("/health", headers=headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://toojunto.example"


def test_api_documentation_is_enabled_in_development():
    config = Settings(_env_file=None, app_env="development")
    client = TestClient(create_app(config))

    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_api_documentation_is_disabled_by_default_in_production():
    client = TestClient(create_app(production_settings()))
    headers = {"Host": "toojunto.example"}

    assert client.get("/docs", headers=headers).status_code == 404
    assert client.get("/redoc", headers=headers).status_code == 404
    assert client.get("/openapi.json", headers=headers).status_code == 404
