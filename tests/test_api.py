from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_rejects_empty_description() -> None:
    response = client.post("/predict", json={"subject": "", "description": ""})
    assert response.status_code == 400
    assert "more detailed description" in response.json()["detail"]
