# src/train.py
import os
import datetime
import subprocess
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import mlflow
import mlflow.sklearn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Config ---
MODEL_DIR = "models"
MODEL_PREFIX = "model"
MODEL_VERSION_FILE = "model_version.txt"
DATA_URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/heart-disease.csv"
# Note: alternative datasets exist; this CSV has common heart-disease columns.

# --- Helpers ---
def get_git_sha():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        return sha
    except Exception:
        return "nogit"

def ensure_dirs():
    os.makedirs(MODEL_DIR, exist_ok=True)

def load_data():
    # read CSV from UCI heart disease dataset
    # The Cleveland dataset has 14 attributes but no header
    column_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                   'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
    df = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data', 
                     header=None, names=column_names)
    # Replace '?' with NaN
    df = df.replace('?', np.nan)
    return df

def preprocess(df):
    # Basic preprocessing: drop NA, do minimal encoding.
    df = df.dropna().reset_index(drop=True)
    # Convert columns to numeric
    for col in df.columns:
        if col != 'target':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna().reset_index(drop=True)
    
    # The target column is already named 'target'
    target_col = 'target'
    X = df.drop(columns=[target_col])
    y = df[target_col].apply(lambda v: 1 if v > 0 else 0)  # ensure binary 0/1
    
    # Keep numeric features only (simple)
    X = X.select_dtypes(include=[np.number]).fillna(0)
    return X, y

def train_and_save(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Set MLflow experiment
    mlflow.set_experiment("heart-disease-prediction")
    
    with mlflow.start_run():
        # Model parameters
        n_estimators = 100
        random_state = 42
        max_depth = 10
        
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("test_size", 0.2)
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=n_estimators, 
            random_state=random_state,
            max_depth=max_depth
        )
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("train_samples", len(X_train))
        mlflow.log_metric("test_samples", len(X_test))
        
        # Log model
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name="heart-disease-model"
        )
        
        # Versioning
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        sha = get_git_sha()
        version = f"{timestamp}-{sha}"
        model_fname = f"{MODEL_PREFIX}-{version}.joblib"
        model_path = os.path.join(MODEL_DIR, model_fname)

        # Save locally as well
        model_data = {
            "model": model, 
            "meta": {
                "accuracy": float(acc), 
                "version": version, 
                "trained_at": timestamp,
                "features": list(X.columns),
                "n_features": len(X.columns)
            }
        }
        joblib.dump(model_data, model_path)

        # Save as latest
        latest_path = os.path.join(MODEL_DIR, "model-latest.joblib")
        joblib.dump(model, latest_path)

        # Save version
        with open(MODEL_VERSION_FILE, "w") as f:
            f.write(version)

        logger.info(f"Saved model to: {model_path}")
        logger.info(f"Accuracy on holdout set: {acc:.4f}")
        logger.info(f"Version: {version}")
        logger.info(f"MLflow run ID: {mlflow.active_run().info.run_id}")
        
        return model, acc, version

def main():
    ensure_dirs()
    df = load_data()
    X, y = preprocess(df)
    train_and_save(X, y)

if __name__ == "__main__":
    main()
