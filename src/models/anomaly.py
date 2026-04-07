import logging
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

def train_isolation_forest() -> None:
    """Train Isolation Forest and save to disk."""
    train_path = PROCESSED_DATA_DIR / "train.parquet"
    if not train_path.exists():
        raise FileNotFoundError(f"Training data not found at {train_path}.")
        
    logger.info("Loading training data for Isolation Forest...")
    train_df = pd.read_parquet(train_path)
    X_train = train_df.drop(columns=["Class"])
    
    logger.info("Training Isolation Forest with contamination=0.002...")
    iso_forest = IsolationForest(contamination=0.002, random_state=42, n_jobs=-1)
    iso_forest.fit(X_train)
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / "isolation_forest.pkl"
    
    with open(model_path, "wb") as f:
        pickle.dump(iso_forest, f)
        
    logger.info(f"Isolation Forest model saved to {model_path}.")

if __name__ == "__main__":
    train_isolation_forest()
