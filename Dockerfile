# Multi-stage Dockerfile for MLOps Heart Disease Prediction
FROM python:3.10-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY model_version.txt .

# Ensure models directory exists
RUN mkdir -p /app/models

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Add local packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI application
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
