"""
Configuration settings for the MLOps project
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Model configuration
MODEL_CONFIG = {
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42,
        "min_samples_split": 2,
        "min_samples_leaf": 1
    }
}

# Data configuration
DATA_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "stratify": True,
    "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
}

# API configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": False,
    "log_level": "info"
}

# MLflow configuration
MLFLOW_CONFIG = {
    "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"),
    "experiment_name": "heart-disease-prediction",
    "model_name": "heart-disease-model"
}

# Monitoring configuration
MONITORING_CONFIG = {
    "metrics_port": 8001,
    "log_level": "INFO",
    "prometheus_pushgateway": os.getenv("PROMETHEUS_PUSHGATEWAY", None)
}

# Docker configuration
DOCKER_CONFIG = {
    "image_name": "heart-disease-prediction",
    "tag": "latest",
    "port": 8000
}

# Feature names (in order)
FEATURE_NAMES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", 
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

# Feature descriptions
FEATURE_DESCRIPTIONS = {
    "age": "Age in years",
    "sex": "Sex (1 = male; 0 = female)",
    "cp": "Chest pain type (0-3)",
    "trestbps": "Resting blood pressure (in mm Hg)",
    "chol": "Serum cholesterol in mg/dl",
    "fbs": "Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)",
    "restecg": "Resting electrocardiographic results (0-2)",
    "thalach": "Maximum heart rate achieved",
    "exang": "Exercise induced angina (1 = yes; 0 = no)",
    "oldpeak": "ST depression induced by exercise relative to rest",
    "slope": "Slope of the peak exercise ST segment (0-2)",
    "ca": "Number of major vessels (0-4) colored by fluoroscopy",
    "thal": "Thalassemia (0 = normal; 1 = fixed defect; 2 = reversable defect)"
}

# Model performance thresholds
PERFORMANCE_THRESHOLDS = {
    "min_accuracy": 0.75,
    "min_precision": 0.70,
    "min_recall": 0.70,
    "max_inference_time_ms": 100
}

# Environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)