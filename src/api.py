"""
FastAPI application for heart disease prediction model serving.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import logging
import os
from datetime import datetime
from typing import Dict, Any
import mlflow
import mlflow.sklearn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Heart Disease Prediction API",
    description="ML model for predicting heart disease risk",
    version="1.0.0"
)

# Pydantic models for request/response
class HeartDiseaseInput(BaseModel):
    age: int = Field(..., description="Age in years", ge=29, le=77)
    sex: int = Field(..., description="Sex (1 = male; 0 = female)")
    cp: int = Field(..., description="Chest pain type (0-3)")
    trestbps: int = Field(..., description="Resting blood pressure", ge=94, le=200)
    chol: int = Field(..., description="Serum cholesterol in mg/dl", ge=126, le=564)
    fbs: int = Field(..., description="Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)")
    restecg: int = Field(..., description="Resting electrocardiographic results (0-2)")
    thalach: int = Field(..., description="Maximum heart rate achieved", ge=71, le=202)
    exang: int = Field(..., description="Exercise induced angina (1 = yes; 0 = no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise", ge=0.0, le=6.2)
    slope: int = Field(..., description="Slope of the peak exercise ST segment (0-2)")
    ca: int = Field(..., description="Number of major vessels colored by fluoroscopy (0-4)")
    thal: int = Field(..., description="Thalassemia (0-3)")

class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="Prediction (0 = no disease, 1 = disease)")
    probability: float = Field(..., description="Probability of heart disease")
    model_version: str = Field(..., description="Model version used")
    timestamp: str = Field(..., description="Prediction timestamp")

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
    timestamp: str

# Global variables for model
model = None
model_version = "unknown"

def load_model():
    """Load the trained model"""
    global model, model_version
    try:
        # Try to load from MLflow first
        try:
            model_uri = "models:/heart-disease-model/latest"
            model = mlflow.sklearn.load_model(model_uri)
            model_version = "mlflow-latest"
            logger.info(f"Loaded model from MLflow: {model_uri}")
        except Exception as e:
            logger.warning(f"Could not load from MLflow: {e}")
            # Fallback to local file
            model_path = "models/model-latest.joblib"
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                # Try to get version from file
                version_path = "model_version.txt"
                if os.path.exists(version_path):
                    with open(version_path, 'r') as f:
                        model_version = f.read().strip()
                else:
                    model_version = "v1.0.0"
                logger.info(f"Loaded model from local file: {model_path}")
            else:
                raise FileNotFoundError("No model file found")
        
        logger.info(f"Model loaded successfully. Version: {model_version}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False

# Load model on startup
@app.on_event("startup")
async def startup_event():
    """Load model when the API starts"""
    if not load_model():
        logger.warning("API started without a model. Predictions will fail.")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Heart Disease Prediction API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        version=model_version,
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: HeartDiseaseInput):
    """Make a heart disease prediction"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert input to numpy array
        features = np.array([[
            input_data.age,
            input_data.sex,
            input_data.cp,
            input_data.trestbps,
            input_data.chol,
            input_data.fbs,
            input_data.restecg,
            input_data.thalach,
            input_data.exang,
            input_data.oldpeak,
            input_data.slope,
            input_data.ca,
            input_data.thal
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]  # Probability of class 1 (disease)
        
        # Log prediction for monitoring
        logger.info(f"Prediction made: {prediction}, Probability: {probability:.3f}")
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability),
            model_version=model_version,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/model-info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": type(model).__name__,
        "version": model_version,
        "features": [
            "age", "sex", "cp", "trestbps", "chol", "fbs", 
            "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ],
        "target": "heart_disease (0: no disease, 1: disease)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)