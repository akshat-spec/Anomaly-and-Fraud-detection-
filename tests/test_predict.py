"""Unit testing suite for FastAPI Prediction Routes."""

from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from src.api.main import app

from contextlib import asynccontextmanager

def get_mock_model():
    mock_model = MagicMock()
    mock_model.predict.return_value = {
        "fraud": False,
        "xgb_score": 0.12,
        "iso_score": 1,
        "confidence": 0.88
    }
    return mock_model

@asynccontextmanager
async def override_lifespan(app_instance):
    app_instance.state.model = get_mock_model()
    app_instance.state.start_time = 0.0
    yield

app.router.lifespan_context = override_lifespan

@pytest.fixture
def mock_ensemble_state():
    """Access the dynamically loaded mock model."""
    return getattr(app.state, "model", None) or get_mock_model()


@pytest.mark.asyncio
async def test_predict_endpoint_success(mock_redis, mock_get_user_features, mock_db_session, mock_kafka_producer, mock_ensemble_state):
    """Ensure predictable REST execution producing non-fraud mapping natively."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/api/v1/predict", json={
            "transaction_id": "tx_req_1",
            "user_id": "usr_99",
            "timestamp": "2023-11-01T12:00:00Z",
            "amount": 250.0
        })

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["transaction_id"] == "tx_req_1"
    assert data["fraud"] is False
    assert "latency_ms" in data


@pytest.mark.asyncio
async def test_predict_endpoint_fraudulent(mock_redis, mock_get_user_features, mock_db_session, mock_kafka_producer, mock_ensemble_state):
    """Ensure predictable REST execution producing Fraud signals properly triggering Kafka alerts explicitly."""
    mock_ensemble_state.predict.return_value = {
        "fraud": True,
        "xgb_score": 0.95,
        "iso_score": -1,
        "confidence": 0.95
    }

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/api/v1/predict", json={
            "transaction_id": "tx_req_2",
            "user_id": "usr_100",
            "timestamp": "2024-01-01T08:30:00Z",
            "amount": 10000.0,
            "v1": -5.0
        })

    assert response.status_code == 200
    data = response.json()
    assert data["fraud"] is True
    assert data["confidence"] == 0.95
    
    # Verify Kafka publisher dynamically called
    mock_kafka_producer.return_value.produce.assert_called_once()


@pytest.mark.asyncio
async def test_predict_validation_error():
    """Ensure negative transactions reject gracefully with 422 Unprocessable Entity."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/api/v1/predict", json={
            "transaction_id": "tx_req_3",
            "user_id": "usr_101",
            "timestamp": "2024-01-01T08:30:00Z",
            "amount": -50.0  # Invalid amount defined deliberately
        })

    assert response.status_code == 422
