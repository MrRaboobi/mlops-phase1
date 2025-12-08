"""Load environment early; ignore E402 for import order.

We intentionally load .env before importing app routers to ensure
environment variables are available at import-time.
"""

# ruff: noqa: E402
from dotenv import load_dotenv
import os
import warnings
import logging
from src.utils.model_loader import get_model

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
# Allow requests from frontend container and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://frontend:80",  # Frontend container service name
        "http://heartsight_frontend:80",  # Frontend container name
        # For production/AWS, you may want to use environment variables
        # or allow all origins in development: ["*"]
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
    """Initialize model and monitoring on startup."""
    print("=" * 60)
    print("🚀 HEARTSIGHT API Starting...")
    print("=" * 60)

    # Start Prometheus metrics server on port 9000
    try:
        from src.monitoring.prometheus_metrics import start_prometheus_metrics
        import threading

        metrics_thread = threading.Thread(
            target=lambda: start_prometheus_metrics(port=9000, sleep_interval=None),
            daemon=True,
        )
        metrics_thread.start()
        print("✅ Prometheus metrics server started on port 9000")
    except Exception as e:
        print(f"⚠️  Could not start Prometheus metrics: {e}")

    # Check if model exists, if not, train automatically
    model_name = os.getenv("MLFLOW_MODEL_NAME", "heartsight_xgb_v1")
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")

    from src.utils.model_loader import model_exists_in_registry

    try:
        model_exists = model_exists_in_registry(
            model_name=model_name, tracking_uri=tracking_uri
        )

        if not model_exists:
            print("=" * 60)
            print("⚠️  Model not found in registry.")
            print("🚀 Starting automatic training...")
            print("   This may take several minutes. Please wait...")
            print("=" * 60)

            # Import and run training synchronously
            training_success = False
            try:
                from src.pipeline.train import main as train_main

                # Run training (this will block until complete)
                train_main()
                training_success = True

            except (MemoryError, OSError) as mem_error:
                print("=" * 60)
                print(f"❌ Training failed due to memory error: {mem_error}")
                print("   The dataset is too large for available memory.")
                print("   Solutions:")
                print(
                    "   1. Increase Docker memory limit (Docker Desktop -> Settings -> Resources)"
                )
                print("   2. Use a smaller training dataset")
                print("   3. Train manually with: python manage.py train")
                print("=" * 60)
            except FileNotFoundError as data_error:
                print("=" * 60)
                print(f"❌ Training data not found: {data_error}")
                print("   Please ensure training data exists in data/raw/")
                print("=" * 60)
            except Exception as train_error:
                print("=" * 60)
                print(f"❌ Training failed: {train_error}")
                print("   You can try training manually: python manage.py train")
                print("=" * 60)

            if training_success:
                print("=" * 60)
                print("✅ Training completed successfully!")
                print("   Loading model into memory...")
                print("=" * 60)

                # Clear model cache to force reload
                import src.utils.model_loader as model_loader_module

                model_loader_module._model = None
                model_loader_module._class_names = None
    except Exception as check_error:
        print(f"⚠️  Could not check model registry: {check_error}")

    # Try to load the model
    try:
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
            print(
                "⚠️  Model not loaded. It may still be training or needs manual training."
            )
            print("   Run: python manage.py train")
    except Exception as e:
        print(f"⚠️  Model will load on first request: {e}")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to HEARTSIGHT API", "tracking_uri": mlflow_uri}
