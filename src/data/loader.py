import logging
import os
import zipfile
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
from kaggle.api.kaggle_api_extended import KaggleApi

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATASET_NAME = "mlg-ulb/creditcardfraud"
CSV_FILE_NAME = "creditcard.csv"

def download_data() -> Path:
    """Download the dataset from Kaggle and unzip it if not already cached."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RAW_DATA_DIR / CSV_FILE_NAME
    
    if csv_path.exists():
        logger.info(f"Dataset already exists at {csv_path}. Skipping download.")
        return csv_path

    logger.info(f"Authenticating with Kaggle API...")
    api = KaggleApi()
    api.authenticate()
    
    logger.info(f"Downloading dataset {DATASET_NAME} to {RAW_DATA_DIR}...")
    api.dataset_download_files(DATASET_NAME, path=str(RAW_DATA_DIR), unzip=True)
    
    if csv_path.exists():
        logger.info("Download and extraction complete.")
    else:
        raise FileNotFoundError(f"Expected {CSV_FILE_NAME} not found after extraction.")
        
    return csv_path

def split_and_save_data(csv_path: Path) -> None:
    """Read data, perform 70/15/15 stratified split, and save as parquet."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    if "Class" not in df.columns:
        raise ValueError("Expected 'Class' column in dataset for stratification.")
        
    logger.info("Splitting data (70% train, 15% val, 15% test) stratified by 'Class'...")
    # First split: 70% train, 30% temp
    train_df, temp_df = train_test_split(
        df, test_size=0.30, stratify=df["Class"], random_state=42
    )
    # Second split: 15% val, 15% test (which is 50% of the 30% temp)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["Class"], random_state=42
    )
    
    train_path = PROCESSED_DATA_DIR / "train.parquet"
    val_path = PROCESSED_DATA_DIR / "val.parquet"
    test_path = PROCESSED_DATA_DIR / "test.parquet"
    
    logger.info(f"Saving splits to {PROCESSED_DATA_DIR}...")
    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)
    
    logger.info("Data splits saved successfully.")

def main():
    try:
        csv_path = download_data()
        split_and_save_data(csv_path)
        logger.info("Data loading pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
