"""Load environment early; ignore E402 for import order.

We intentionally load .env before importing app routers to ensure
environment variables are available at import-time.
"""

# ruff: noqa: E402
from dotenv import load_dotenv
import os
import warnings
import logging

load_dotenv()

# Suppress ALL warnings for cleaner logs
warnings.filterwarnings("ignore")
logging.getLogger("mlflow").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import health, predict, chat

# Optional: Only import storage router if boto3 is available
try:
    from src.api.routers import storage

    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False

app = FastAPI(
    title="HEARTSIGHT API",
    description="AI-powered ECG monitoring and early warning system with MLOps integration.",
    version="2.0.0",
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    # Allow common local/dev origins. Add more if you access via another host/IP.
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(chat.router)
if STORAGE_AVAILABLE:
    app.include_router(storage.router)


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    print("=" * 60)
    print("🚀 HEARTSIGHT API Starting...")
    print("=" * 60)
    try:
        from src.utils.model_loader import get_model

        # Suppress all output during model loading
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            model, class_names = get_model(raise_on_error=False)
        finally:
            sys.stdout = old_stdout

        if model is not None:
            print(f"✅ Model ready. Classes: {class_names}")
            print("=" * 60)
            print("✅ API Ready! Listening on http://127.0.0.1:8000")
            print("=" * 60)
        else:
            print("⚠️  Model not found. Train first: python manage.py train")
    except Exception as e:
        print(f"⚠️  Model will load on first request: {e}")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to HEARTSIGHT API", "tracking_uri": mlflow_uri}
