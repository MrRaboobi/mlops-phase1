"""Load environment early; ignore E402 for import order.

We intentionally load .env before importing app routers to ensure
environment variables are available at import-time.
"""

# ruff: noqa: E402
from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from src.api.routers import health, predict, storage

app = FastAPI(
    title="Federated ECGGuard API",
    description="Secure, MLOps-ready API with environment-based configuration.",
    version="1.0.0",
)

mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
print(f"MLflow Tracking URI: {mlflow_uri}")
print(os.getenv("PROMETHEUS_PORT"))
print(os.getenv("SECRET_KEY"))

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(storage.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Federated ECGGuard API", "tracking_uri": mlflow_uri}
