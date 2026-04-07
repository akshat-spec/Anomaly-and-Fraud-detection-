import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering transformations."""
    logger.info("Applying feature engineering transformations...")
    df = df.copy()
    
    # 1. Log transform Amount (adding a small epsilon for zero amounts)
    logger.info("Log-transforming Amount...")
    df['Amount_log'] = np.log1p(df['Amount'])
    
    # 2. Time of day from Time (seconds from start, 86400 sec per day)
    logger.info("Extracting time-of-day features...")
    df['Time_of_day_hour'] = (df['Time'] % 86400) / 3600.0
    
    # 3. Rolling statistics over the last hour (3600 seconds)
    logger.info("Computing rolling statistics for Amount over a 1-hour window...")
    df['TimeDelta'] = pd.to_timedelta(df['Time'], unit='s')
    df = df.sort_values('TimeDelta')
    
    df['Amount_rolling_mean_1h'] = df.rolling('1h', on='TimeDelta')['Amount'].mean()
    df['Amount_rolling_std_1h'] = df.rolling('1h', on='TimeDelta')['Amount'].std().fillna(0)
    
    df = df.drop(columns=['TimeDelta'])
    return df

def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    train_path = PROCESSED_DATA_DIR / "train.parquet"
    val_path = PROCESSED_DATA_DIR / "val.parquet"
    test_path = PROCESSED_DATA_DIR / "test.parquet"
    
    if not train_path.exists():
        raise FileNotFoundError(f"Training data not found at {train_path}. Run loader first.")
        
    logger.info("Loading splits...")
    train_df = pd.read_parquet(train_path)
    val_df = pd.read_parquet(val_path)
    test_df = pd.read_parquet(test_path)
    
    train_df = engineer_features(train_df)
    val_df = engineer_features(val_df)
    test_df = engineer_features(test_df)
    
    # Fit StandardScaler on train ONLY
    # Features to scale: exclude 'Class'
    features_to_scale = [c for c in train_df.columns if c != 'Class']
    logger.info("Fitting StandardScaler on training data...")
    scaler = StandardScaler()
    train_df[features_to_scale] = scaler.fit_transform(train_df[features_to_scale])
    
    # Save the scaler
    scaler_path = MODELS_DIR / "scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    logger.info(f"Scaler saved to {scaler_path}")
    
    # Transform val and test
    logger.info("Applying scaler to validation and test sets...")
    val_df[features_to_scale] = scaler.transform(val_df[features_to_scale])
    test_df[features_to_scale] = scaler.transform(test_df[features_to_scale])
    
    # Save engineered data (overwriting the raw splits)
    logger.info("Saving engineered splits...")
    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)
    
    logger.info("Feature engineering completed successfully.")

if __name__ == "__main__":
    main()
