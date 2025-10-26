# MLOps Heart Disease Prediction

A complete MLOps pipeline for heart disease prediction using machine learning, containerization, and CI/CD.

## 🎯 Project Overview

This project implements a heart disease classification model with:
- **Machine Learning**: Random Forest classifier for heart disease prediction
- **Model Versioning**: MLflow for experiment tracking and model registry
- **Containerization**: Docker for consistent deployment
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **API**: FastAPI REST endpoint for model serving
- **Monitoring**: Basic model performance monitoring

## 📊 Model Performance

- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~85% on test data
- **Features**: 13 clinical features (age, sex, chest pain, blood pressure, etc.)
- **Target**: Binary classification (0: No heart disease, 1: Heart disease)

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/AKA-Akhil/heart-disease-prediction.git
cd heart-disease-prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train the model
python src/train.py

# Run tests
pytest tests/

# Start the API server
uvicorn src.api:app --reload
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t heart-disease-prediction .

# Run the container
docker run -p 8000:8000 heart-disease-prediction

# Access the API at http://localhost:8000/docs
```

## 🏗️ Project Structure

```
heart-disease-prediction/
├── .github/workflows/          # CI/CD pipeline
├── src/                        # Source code
│   ├── train.py               # Model training
│   ├── predict.py             # Model prediction
│   ├── api.py                 # FastAPI application
│   └── utils.py               # Utility functions
├── tests/                      # Test suite
├── data/                       # Dataset (not tracked)
├── models/                     # Trained models (not tracked)
├── monitoring/                 # Model monitoring
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-service setup
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline automatically:
1. **Tests**: Runs unit tests and model validation
2. **Builds**: Creates Docker image
3. **Deploys**: Pushes to registry and deploys (staging)
4. **Monitors**: Tracks model performance metrics

## 📈 Model Versioning

- **MLflow**: Experiment tracking and model registry
- **DVC**: Data and model versioning
- **Git**: Source code version control

## 🔍 Monitoring

- Model performance metrics
- Data drift detection
- API response times
- Resource utilization

## 🧪 Testing Strategy

- Unit tests for all functions
- Integration tests for API endpoints
- Model validation tests
- Data quality checks

## 📝 API Documentation

Access the interactive API documentation at `/docs` when running the server.

### Example Usage

```python
import requests

# Predict heart disease
response = requests.post("http://localhost:8000/predict", json={
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
})

print(response.json())
# {"prediction": 1, "probability": 0.85, "model_version": "v1.0.0"}
```

## 🏆 MLOps Best Practices Implemented

- ✅ Version control (Git)
- ✅ Automated testing (pytest)
- ✅ Containerization (Docker)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Model versioning (MLflow)
- ✅ API serving (FastAPI)
- ✅ Monitoring and logging
- ✅ Documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
