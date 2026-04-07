import json
import logging
import pickle
from pathlib import Path
from typing import Dict, Union

import pandas as pd
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

class FraudEnsemble:
    def __init__(self) -> None:
        xgb_path = MODELS_DIR / "xgboost_fraud.pkl"
        iso_path = MODELS_DIR / "isolation_forest.pkl"
        
        if not xgb_path.exists() or not iso_path.exists():
            raise FileNotFoundError("Models not found. Run training pipeline first.")
            
        with open(xgb_path, "rb") as f:
            self.xgb_model = pickle.load(f)
            
        with open(iso_path, "rb") as f:
            self.iso_model = pickle.load(f)
            
    def predict(self, features: pd.DataFrame) -> Dict[str, Union[bool, float, int]]:
        """
        Run inference on a single record DataFrame.
        Produces combined decision: XGB score > 0.7 OR Isolation Forest flags as anomaly (-1).
        """
        if len(features) != 1:
            raise ValueError("Predict function expects a 1-row DataFrame for a single response.")
            
        dtest = xgb.DMatrix(features)
        xgb_score = float(self.xgb_model.predict(dtest)[0])
        iso_score = int(self.iso_model.predict(features)[0])
        
        is_fraud = bool(xgb_score > 0.7 or iso_score == -1)
        
        # Simple pseudo-confidence mapping logic 
        if is_fraud:
            confidence = max(xgb_score, 0.9 if iso_score == -1 else xgb_score)
        else:
            confidence = 1.0 - xgb_score
            
        return {
            "fraud": is_fraud,
            "xgb_score": xgb_score,
            "iso_score": iso_score,
            "confidence": confidence
        }

def evaluate_on_test() -> None:
    """Evaluate ensemble logic on the top records of test set."""
    test_path = PROCESSED_DATA_DIR / "test.parquet"
    if not test_path.exists():
        raise FileNotFoundError(f"Test data not found at {test_path}.")
        
    logger.info("Loading test data...")
    test_df = pd.read_parquet(test_path)
    X_test = test_df.drop(columns=["Class"])
    y_test = test_df["Class"].tolist()
    
    ensemble = FraudEnsemble()
    
    logger.info("Running ensemble inference check on first 5 samples from test set...")
    for i in range(5):
        record = X_test.iloc[[i]]
        true_label = y_test[i]
        
        result = ensemble.predict(record)
        logger.info(f"Sample {i+1} - True Class: {true_label} | Ensemble Result: {json.dumps(result)}")
        
if __name__ == "__main__":
    evaluate_on_test()
