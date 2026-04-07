import logging
import os
import pickle
from pathlib import Path
from typing import Tuple

import mlflow
import numpy as np
import optuna
import pandas as pd
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_recall_curve, auc

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment("Fraud-Detection-XGBoost")

def load_data() -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Load train, val, and test splits from parquet."""
    train_path = PROCESSED_DATA_DIR / "train.parquet"
    if not train_path.exists():
        raise FileNotFoundError("Processed datasets not found.")
        
    train_df = pd.read_parquet(train_path)
    val_df = pd.read_parquet(PROCESSED_DATA_DIR / "val.parquet")
    test_df = pd.read_parquet(PROCESSED_DATA_DIR / "test.parquet")
    
    X_train, y_train = train_df.drop(columns=["Class"]), train_df["Class"]
    X_val, y_val = val_df.drop(columns=["Class"]), val_df["Class"]
    X_test, y_test = test_df.drop(columns=["Class"]), test_df["Class"]
    
    return X_train, y_train, X_val, y_val, X_test, y_test

def apply_smote(X_train: pd.DataFrame, y_train: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    """Apply SMOTE to handle class imbalance on training set."""
    logger.info("Applying SMOTE to training data...")
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    return X_resampled, y_resampled

def compute_pr_auc(y_true: pd.Series, y_pred_proba: np.ndarray) -> float:
    """Compute Precision-Recall AUC."""
    precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
    return auc(recall, precision)

def train_and_optimize() -> None:
    """Run Optuna hyperparameter search, log to MLflow, and evaluate on test set."""
    X_train, y_train, X_val, y_val, X_test, y_test = load_data()
    X_train_res, y_train_res = apply_smote(X_train, y_train)
    
    def objective(trial: optuna.Trial) -> float:
        params = {
            "objective": "binary:logistic",
            "eval_metric": "aucpr",
            "booster": "gbtree",
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
            "random_state": 42
        }
        
        with mlflow.start_run(nested=True):
            mlflow.log_params(params)
            
            dtrain = xgb.DMatrix(X_train_res, label=y_train_res)
            dval = xgb.DMatrix(X_val, label=y_val)
            
            model = xgb.train(
                params,
                dtrain,
                num_boost_round=100,
                evals=[(dval, "val")],
                early_stopping_rounds=10,
                verbose_eval=False
            )
            
            preds = model.predict(dval)
            pr_auc = compute_pr_auc(y_val, preds)
            f1 = f1_score(y_val, (preds > 0.5).astype(int))
            
            mlflow.log_metric("val_pr_auc", pr_auc)
            mlflow.log_metric("val_f1", f1)
            
            return pr_auc
            
    logger.info("Starting Optuna hyperparameter optimization (50 trials)...")
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=50)
    
    best_params = study.best_params
    best_params["objective"] = "binary:logistic"
    best_params["eval_metric"] = "aucpr"
    
    logger.info(f"Best params found: {best_params}")
    
    with mlflow.start_run(run_name="best_model"):
        mlflow.log_params(best_params)
        
        dtrain = xgb.DMatrix(X_train_res, label=y_train_res)
        dval = xgb.DMatrix(X_val, label=y_val)
        dtest = xgb.DMatrix(X_test, label=y_test)
        
        logger.info("Training best model...")
        model = xgb.train(
            best_params,
            dtrain,
            num_boost_round=300,
            evals=[(dtrain, "train"), (dval, "val")],
            early_stopping_rounds=20,
            verbose_eval=50
        )
        
        logger.info("Evaluating on test set...")
        test_preds_proba = model.predict(dtest)
        
        # Determine best threshold based on validation data for better F1 (optional) 
        # Using 0.5 per standard practice, but PR curve lets us pick optimal.
        # We will use 0.5 here.
        test_preds = (test_preds_proba > 0.5).astype(int)
        
        pr_auc = compute_pr_auc(y_test, test_preds_proba)
        f1 = f1_score(y_test, test_preds)
        cm = confusion_matrix(y_test, test_preds)
        cr = classification_report(y_test, test_preds)
        
        logger.info(f"Test PR-AUC: {pr_auc}")
        logger.info(f"Test F1: {f1}")
        logger.info(f"Confusion Matrix:\n{cm}")
        logger.info(f"Classification Report:\n{cr}")
        
        mlflow.log_metric("test_pr_auc", pr_auc)
        mlflow.log_metric("test_f1", f1)
        
        # Save model Locally
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_path = MODELS_DIR / "xgboost_fraud.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
            
        mlflow.log_artifact(str(model_path))
        logger.info(f"Model saved locally to {model_path}.")
        
        # Register in MLflow Model Registry
        logger.info("Registering model in MLflow...")
        mlflow.xgboost.log_model(model, "xgboost-model", registered_model_name="XGBoostFraudModel")

if __name__ == "__main__":
    train_and_optimize()
