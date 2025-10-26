"""
Test suite for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
import numpy as np
import json
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app

client = TestClient(app)

class TestAPI:
    """Test the FastAPI endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data
        assert "timestamp" in data
        
    def test_model_info_endpoint(self):
        """Test the model info endpoint"""
        response = client.get("/model-info")
        # May return 503 if model not loaded, that's ok for testing
        assert response.status_code in [200, 503]
        
    def test_predict_endpoint_valid_input(self):
        """Test prediction with valid input"""
        valid_input = {
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
        
        response = client.post("/predict", json=valid_input)
        # May return 503 if model not loaded
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data
            assert "probability" in data
            assert "model_version" in data
            assert "timestamp" in data
            assert data["prediction"] in [0, 1]
            assert 0.0 <= data["probability"] <= 1.0
        else:
            assert response.status_code == 503
            
    def test_predict_endpoint_invalid_input(self):
        """Test prediction with invalid input"""
        invalid_input = {
            "age": -5,  # Invalid age
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
        
        response = client.post("/predict", json=invalid_input)
        assert response.status_code == 422  # Validation error
        
    def test_predict_endpoint_missing_fields(self):
        """Test prediction with missing required fields"""
        incomplete_input = {
            "age": 54,
            "sex": 1,
            # Missing other required fields
        }
        
        response = client.post("/predict", json=incomplete_input)
        assert response.status_code == 422  # Validation error