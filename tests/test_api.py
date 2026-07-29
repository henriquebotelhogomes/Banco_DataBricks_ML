"""Testes da Credit Risk Scoring API (spec seção 14)."""

from fastapi.testclient import TestClient

from src.api.main import app  # pytest executado a partir da raiz do repositório

client = TestClient(app)

VALID_PAYLOAD = {
    "client_id": "12345",
    "income": 5000.0,
    "age": 30,
    "avg_spend_90d": 1250.50,
    "total_late_payments": 0,
    "current_bureau_score": 0.72,
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_prediction_valid_data():
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert "probability_of_default" in body
    assert 0.0 <= body["probability_of_default"] <= 1.0
    assert body["decision"] in {"APPROVED", "REJECTED"}
    assert len(body["explanation"]) == 3


def test_prediction_low_risk_is_approved():
    payload = {**VALID_PAYLOAD, "current_bureau_score": 0.95, "total_late_payments": 0}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "APPROVED"


def test_prediction_high_risk_is_rejected():
    payload = {**VALID_PAYLOAD, "current_bureau_score": 0.10, "total_late_payments": 8}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "REJECTED"


def test_prediction_invalid_age_rejected_by_validation():
    payload = {**VALID_PAYLOAD, "age": 15}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Pydantic: age >= 18


def test_prediction_invalid_score_rejected_by_validation():
    payload = {**VALID_PAYLOAD, "current_bureau_score": 750}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Pydantic: 0 <= score <= 1


def test_prediction_missing_field_rejected_by_validation():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "income"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
