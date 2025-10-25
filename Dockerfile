# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Ensure models directory exists (train step in CI will provide models artifact)
RUN mkdir -p /app/models

EXPOSE 8501

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false

CMD ["streamlit", "run", "src/predict.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
