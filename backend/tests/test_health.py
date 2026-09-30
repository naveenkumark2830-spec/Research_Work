from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Test health check endpoint GET /api/v1/health."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "hadoop-ai-simulator-backend"


def test_root_endpoint() -> None:
    """Test root endpoint GET /."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("service") == "hadoop-ai-simulator-backend"
    assert data.get("status") == "running"
