"""Tests driving specific Ensemble logic intrinsically overriding Pickled models dynamically."""

from unittest.mock import MagicMock

import pandas as pd

from src.models.ensemble import FraudEnsemble


def setup_mock_ensemble() -> FraudEnsemble:
    """Instantiate FraudEnsemble completely skipping disk loading routines dynamically."""
    wrapper = object.__new__(FraudEnsemble)
    wrapper.xgb_model = MagicMock()
    wrapper.iso_model = MagicMock()
    return wrapper


def test_ensemble_predicts_fraud_from_xgb():
    """Confirm Fraudulent state triggers when XGBoost crosses threshold explicitly."""
    wrapper = setup_mock_ensemble()
    
    wrapper.xgb_model.predict.return_value = [0.85]  # Trigger fraud threshold natively >0.70
    wrapper.iso_model.predict.return_value = [1]     # Normal mapping natively

    df = pd.DataFrame([{"Time": 100.0, "Amount": 500.0}])
    result = wrapper.predict(df)

    assert result["fraud"] is True
    assert result["xgb_score"] == 0.85
    assert result["iso_score"] == 1
    assert result["confidence"] == 0.85


def test_ensemble_predicts_fraud_from_iso():
    """Confirm Fraudulent state strictly triggers sequentially if IsolationForest flags natively."""
    wrapper = setup_mock_ensemble()
    
    wrapper.xgb_model.predict.return_value = [0.45]  # Below typical fraud detection mapping
    wrapper.iso_model.predict.return_value = [-1]    # Anomaly flagged securely

    df = pd.DataFrame([{"Time": 200.0, "Amount": 100.0}])
    result = wrapper.predict(df)

    assert result["fraud"] is True
    assert result["iso_score"] == -1
    # Confidence maps intrinsically tracking maximum available likelihood preserving limits gracefully
    assert result["confidence"] == 0.90


def test_ensemble_predicts_non_fraud():
    """Confirm limits efficiently rejecting fraud markers smoothly."""
    wrapper = setup_mock_ensemble()
    
    wrapper.xgb_model.predict.return_value = [0.15]
    wrapper.iso_model.predict.return_value = [1]

    df = pd.DataFrame([{"Time": 300.0, "Amount": 50.0}])
    result = wrapper.predict(df)

    assert result["fraud"] is False
    assert result["confidence"] == 0.85  # (1 - 0.15) mappings preserved organically
