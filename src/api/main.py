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
    title="HEARTSIGHT API",
    description="AI-powered ECG monitoring and early warning system with MLOps integration.",
    version="2.0.0",
)

mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
print(f"MLflow Tracking URI: {mlflow_uri}")
print(f"Prometheus Port: {os.getenv('PROMETHEUS_PORT', '9000')}")
print(f"App Environment: {os.getenv('APP_ENV', 'development')}")

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(storage.router)


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup (optional - model loads lazily on first request)."""
    try:
        from src.utils.model_loader import get_model

        print("Attempting to load model from MLflow registry...")
        model, class_names = get_model(raise_on_error=False)
        if model is not None:
            print(f"✅ Model loaded successfully. Classes: {class_names}")
        else:
            print(
                "⚠️  Model not found. Train a model first using: python manage.py train"
            )
            print("   Model will be loaded on first prediction request.")
    except Exception as e:
        print(f"⚠️  Model not loaded on startup (will load on first prediction): {e}")
        print("This is normal if no model has been trained yet.")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Federated ECGGuard API", "tracking_uri": mlflow_uri}
