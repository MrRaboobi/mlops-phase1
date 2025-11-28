"""
Model loader utility for loading MLflow-registered models.
Handles lazy loading and caching of the model for API inference.
"""

import os
import mlflow
import mlflow.xgboost
import numpy as np
from typing import Optional, List

# Global model cache
_model: Optional[object] = None
_class_names: Optional[List[str]] = None


def extract_features_from_signal(signal_array):
    """
    Extract statistical features from ECG signal for tree-based models.
    Converts (TimeSteps, 12) array to a flat feature vector.

    Features extracted per channel:
    - Mean, std, min, max
    - Percentiles (25th, 50th, 75th)
    - Additional: range, variance
    """
    features = []

    # For each of the 12 channels
    for channel_idx in range(12):
        channel_data = signal_array[:, channel_idx]

        # Statistical features
        features.extend(
            [
                np.mean(channel_data),
                np.std(channel_data),
                np.min(channel_data),
                np.max(channel_data),
                np.percentile(channel_data, 25),
                np.percentile(channel_data, 50),  # median
                np.percentile(channel_data, 75),
                np.ptp(channel_data),  # range (peak-to-peak)
                np.var(channel_data),  # variance
            ]
        )

    return np.array(features)


def load_model_from_registry(
    model_name: str = "heartsight_xgb_v1",
    stage: str = "Production",
    tracking_uri: Optional[str] = None,
) -> tuple:
    """
    Load model and class names from MLflow Model Registry.

    Args:
        model_name: Name of the registered model
        stage: Model stage (Production, Staging, None)
        tracking_uri: MLflow tracking URI (defaults to file:./mlruns)

    Returns:
        Tuple of (model, class_names)
    """
    global _model, _class_names

    # Set tracking URI if provided, otherwise use default
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    else:
        # Default to local file-based tracking
        mlflow.set_tracking_uri("file:./mlruns")

    try:
        # Load model from registry
        if stage:
            model_uri = f"models:/{model_name}/{stage}"
        else:
            # Get latest version
            model_uri = f"models:/{model_name}/latest"

        print(f"Loading model from: {model_uri}")
        _model = mlflow.xgboost.load_model(model_uri)
        print("✅ Model loaded successfully")

        # Try to load class names from artifacts
        try:
            # Get the latest run for this model
            client = mlflow.tracking.MlflowClient()
            model_version = client.get_latest_versions(
                model_name, stages=[stage] if stage else None
            )[0]
            run_id = model_version.run_id

            # Download class_names.txt artifact
            artifact_path = mlflow.artifacts.download_artifacts(
                run_id=run_id, artifact_path="class_names.txt"
            )

            with open(artifact_path, "r") as f:
                _class_names = [line.strip() for line in f.readlines()]
            print(f"✅ Loaded class names: {_class_names}")

        except Exception as e:
            print(f"⚠️  Could not load class names from artifacts: {e}")
            # Fallback to default class names
            _class_names = ["NORM", "MI", "STTC", "CD", "HYP"]
            print(f"Using default class names: {_class_names}")

        return _model, _class_names

    except Exception as e:
        error_msg = (
            f"❌ Error loading model: {e}\n"
            f"Make sure you have trained and registered a model first.\n"
            f"Run: python manage.py train"
        )
        print(error_msg)
        raise RuntimeError(error_msg) from e


def get_model(raise_on_error: bool = True):
    """
    Get the cached model, loading it if necessary.

    Args:
        raise_on_error: If True, raise exception on error. If False, return None.

    Returns:
        Tuple of (model, class_names) or (None, None) if raise_on_error=False
    """
    global _model, _class_names

    if _model is None:
        # Try to load from environment variables or use defaults
        model_name = os.getenv("MLFLOW_MODEL_NAME", "heartsight_xgb_v1")
        model_stage = os.getenv("MLFLOW_MODEL_STAGE", "Production")
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")

        try:
            _model, _class_names = load_model_from_registry(
                model_name=model_name, stage=model_stage, tracking_uri=tracking_uri
            )
        except Exception:
            if raise_on_error:
                raise
            else:
                return None, None

    return _model, _class_names


def predict_ecg_signal(signal_data: np.ndarray) -> dict:
    """
    Predict ECG class from signal data.

    Args:
        signal_data: ECG signal array of shape (time_steps, 12)

    Returns:
        Dictionary with prediction class, confidence, and probabilities
    """
    model, class_names = get_model()

    # Extract features from signal (same as training)
    if len(signal_data.shape) == 3:
        # If shape is (1, time_steps, 12), squeeze first dimension
        signal_data = signal_data[0]

    # Extract features
    features = extract_features_from_signal(signal_data)
    features = features.reshape(1, -1)  # Reshape to (1, num_features) for prediction

    # Get predictions
    predictions = model.predict_proba(features)[
        0
    ]  # Get probabilities for first (and only) sample
    predicted_class_idx = np.argmax(predictions)
    confidence = float(predictions[predicted_class_idx])
    predicted_class = class_names[predicted_class_idx]

    # Create probability dictionary
    probabilities = {
        class_names[i]: float(predictions[i]) for i in range(len(class_names))
    }

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "probabilities": probabilities,
        "class_index": int(predicted_class_idx),
    }
