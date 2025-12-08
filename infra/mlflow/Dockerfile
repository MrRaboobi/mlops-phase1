# Custom MLflow image with fixed dependencies
# Use Python 3.11 base and install MLflow with compatible dependencies
FROM python:3.11-slim

WORKDIR /mlflow

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install MLflow with compatible dependency versions
RUN pip install --no-cache-dir \
    mlflow==2.15.1 \
    typing_extensions>=4.5.0 \
    "urllib3>=1.26.0,<3.0.0" \
    pydantic \
    pydantic-core

# Create mlruns directory
RUN mkdir -p /mlflow/mlruns

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "sqlite:////mlflow/mlruns/mlflow.db", \
     "--default-artifact-root", "/mlflow/mlruns", \
     "--host", "0.0.0.0", \
     "--port", "5000"]
