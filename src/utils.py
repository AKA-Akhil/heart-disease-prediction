"""
Utility functions for the MLOps project
"""

import logging
import time
import json
import pickle
import joblib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def save_json(data: Dict[str, Any], filepath: Union[str, Path]) -> None:
    """Save data as JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_model(model: Any, filepath: Union[str, Path], metadata: Optional[Dict] = None) -> None:
    """Save model with metadata"""
    model_data = {
        'model': model,
        'metadata': metadata or {},
        'saved_at': datetime.now().isoformat()
    }
    joblib.dump(model_data, filepath)

def load_model(filepath: Union[str, Path]) -> tuple:
    """Load model and metadata"""
    model_data = joblib.load(filepath)
    return model_data['model'], model_data.get('metadata', {})

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate classification metrics"""
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1_score': f1_score(y_true, y_pred, average='weighted')
    }

def create_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Create confusion matrix"""
    return confusion_matrix(y_true, y_pred)

def validate_input_data(data: Dict[str, Any], required_features: list) -> bool:
    """Validate input data for prediction"""
    # Check if all required features are present
    missing_features = set(required_features) - set(data.keys())
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    # Check data types and ranges (basic validation)
    for feature, value in data.items():
        if feature in required_features:
            if not isinstance(value, (int, float)):
                raise ValueError(f"Feature {feature} must be numeric, got {type(value)}")
            if np.isnan(value) or np.isinf(value):
                raise ValueError(f"Feature {feature} contains invalid value: {value}")
    
    return True

def format_prediction_response(prediction: int, probability: float, model_version: str) -> Dict[str, Any]:
    """Format prediction response"""
    return {
        'prediction': int(prediction),
        'probability': float(probability),
        'model_version': model_version,
        'timestamp': datetime.now().isoformat(),
        'risk_level': 'High' if probability > 0.7 else 'Medium' if probability > 0.3 else 'Low'
    }

def measure_inference_time(func):
    """Decorator to measure inference time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        inference_time = time.time() - start_time
        
        if isinstance(result, dict):
            result['inference_time_ms'] = inference_time * 1000
        
        return result
    return wrapper

def create_sample_input() -> Dict[str, Any]:
    """Create a sample input for testing"""
    return {
        "age": 54,
        "sex": 1,
        "cp": 0,
        "trestbps": 140,
        "chol": 239,
        "fbs": 0,
        "restecg": 1,
        "thalach": 160,
        "exang": 0,
        "oldpeak": 1.2,
        "slope": 2,
        "ca": 0,
        "thal": 2
    }

def generate_model_report(model, X_test: pd.DataFrame, y_test: pd.Series, 
                         model_version: str) -> Dict[str, Any]:
    """Generate comprehensive model report"""
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = calculate_metrics(y_test, y_pred)
    cm = create_confusion_matrix(y_test, y_pred)
    
    report = {
        'model_version': model_version,
        'test_samples': len(X_test),
        'metrics': metrics,
        'confusion_matrix': cm.tolist(),
        'feature_importance': None,
        'generated_at': datetime.now().isoformat()
    }
    
    # Add feature importance if available
    if hasattr(model, 'feature_importances_'):
        importance_dict = dict(zip(X_test.columns, model.feature_importances_))
        report['feature_importance'] = sorted(
            importance_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
    
    return report

class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"{self.operation_name} completed in {duration:.3f} seconds")
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0