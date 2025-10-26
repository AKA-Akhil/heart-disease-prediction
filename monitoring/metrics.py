"""
Model monitoring and metrics collection
"""

import time
import logging
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
PREDICTION_COUNTER = Counter('ml_predictions_total', 'Total number of predictions made')
PREDICTION_LATENCY = Histogram('ml_prediction_duration_seconds', 'Time spent on predictions')
MODEL_ACCURACY = Gauge('ml_model_accuracy', 'Current model accuracy')
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])

class ModelMonitor:
    """Monitor model performance and API metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.prediction_count = 0
        self.total_latency = 0.0
        
    def record_prediction(self, latency: float, prediction: int, probability: float):
        """Record a prediction event"""
        PREDICTION_COUNTER.inc()
        PREDICTION_LATENCY.observe(latency)
        
        self.prediction_count += 1
        self.total_latency += latency
        
        logger.info(f"Prediction recorded: {prediction}, prob: {probability:.3f}, latency: {latency:.3f}s")
        
    def record_api_request(self, method: str, endpoint: str, status_code: int):
        """Record an API request"""
        API_REQUESTS.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        
    def update_model_accuracy(self, accuracy: float):
        """Update model accuracy metric"""
        MODEL_ACCURACY.set(accuracy)
        logger.info(f"Model accuracy updated: {accuracy:.3f}")
        
    def get_stats(self):
        """Get monitoring statistics"""
        avg_latency = self.total_latency / self.prediction_count if self.prediction_count > 0 else 0
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_predictions": self.prediction_count,
            "average_latency": avg_latency,
            "predictions_per_minute": (self.prediction_count / uptime) * 60 if uptime > 0 else 0
        }

# Global monitor instance
monitor = ModelMonitor()

def monitor_prediction(func):
    """Decorator to monitor prediction functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            latency = time.time() - start_time
            
            # Extract prediction info if available
            if isinstance(result, dict) and 'prediction' in result:
                monitor.record_prediction(
                    latency=latency,
                    prediction=result['prediction'],
                    probability=result.get('probability', 0.0)
                )
            
            return result
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"Prediction failed after {latency:.3f}s: {e}")
            raise
    return wrapper

def start_metrics_server(port: int = 8001):
    """Start Prometheus metrics server"""
    start_http_server(port)
    logger.info(f"Metrics server started on port {port}")

if __name__ == "__main__":
    # Start metrics server for testing
    start_metrics_server()
    
    # Simulate some metrics
    monitor.record_prediction(0.05, 1, 0.85)
    monitor.record_prediction(0.03, 0, 0.25)
    monitor.update_model_accuracy(0.87)
    
    print("Metrics server running on http://localhost:8001")
    print("Visit http://localhost:8001/metrics to see metrics")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down metrics server")