"""Shared fixtures mimicking Redis Cache and DB states dynamically."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_redis():
    with patch("src.feature_store.redis_client.get_redis", new_callable=AsyncMock) as redis_mock:
        redis_mock.return_value.get.return_value = None  # Ensure caching is bypassed intrinsically
        yield redis_mock


@pytest.fixture
def mock_get_user_features():
    with patch("src.feature_store.redis_client.get_user_features", new_callable=AsyncMock) as feat_mock:
        feat_mock.return_value = {
            "txn_count": 5,
            "mean_amount": 100.0,
            "std_amount": 5.0,
            "max_amount": 120.0
        }
        yield feat_mock


@pytest.fixture
def mock_db_session():
    with patch("src.api.routes.predict.get_session") as session_mock:
        yield session_mock


@pytest.fixture
def mock_kafka_producer():
    with patch("src.api.routes.predict.get_kafka_producer") as kafka_mock:
        yield kafka_mock
