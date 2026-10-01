from fastapi.testclient import TestClient
from app.main import APP_VERSION, app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "toojunto-api",
        "version": "0.3.0",
    }
    assert app.version == APP_VERSION == "0.3.0"


def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
