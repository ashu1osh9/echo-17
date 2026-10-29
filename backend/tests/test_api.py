from fastapi.testclient import TestClient
from app.main import app


def test_health_without_data():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert isinstance(response.json()["data_ready"], bool)


def test_sensor_metadata():
    response = TestClient(app).get("/api/meta")
    assert response.status_code == 200
    assert len(response.json()["sensors"]) == 6
