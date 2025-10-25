# src/train.py
import os
import datetime
import subprocess
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    # versioning
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    sha = get_git_sha()
    version = f"{timestamp}-{sha}"
    model_fname = f"{MODEL_PREFIX}-{version}.joblib"
    model_path = os.path.join(MODEL_DIR, model_fname)

    joblib.dump({"model": model, "meta": {"accuracy": float(acc), "version": version, "trained_at": timestamp}}, model_path)

    # write latest pointer as well for ease
    latest_path = os.path.join(MODEL_DIR, "model-latest.joblib")
    joblib.dump({"model": model, "meta": {"accuracy": float(acc), "version": version, "trained_at": timestamp}}, latest_path)

    with open(MODEL_VERSION_FILE, "w") as f:
        f.write(version)

    print(f"Saved model to: {model_path}")
    print(f"Accuracy on holdout set: {acc:.4f}")
    print(f"Version: {version}")

def main():
    ensure_dirs()
    df = load_data()
    X, y = preprocess(df)
    train_and_save(X, y)

if __name__ == "__main__":
    main()
