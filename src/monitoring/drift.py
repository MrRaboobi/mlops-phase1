"""
Data drift monitoring utilities for HEARTSIGHT.

This module uses Evidently to:
- Build a reference baseline from training ECG features
- Compare incoming ECG signals / feature batches against the baseline
- Generate HTML drift reports for offline review

It is designed to be run as an offline job (e.g., cron / pipeline step),
but the helper function `compute_single_ecg_drift_score` can be called
from online code if needed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset


DRIFT_DATA_DIR = Path("data/drift")
DRIFT_DATA_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_FEATURES_PATH = DRIFT_DATA_DIR / "reference_features.parquet"


def build_reference_baseline(max_samples: int = 500) -> pd.DataFrame:
    """
    Build reference baseline features from the training pipeline.

    We reuse the feature extraction logic from `src.pipeline.train`.
    The resulting feature matrix is persisted to `data/drift/reference_features.parquet`.
    """

    from src.pipeline.train import load_and_process_data

    X, _, _ = load_and_process_data()
    if max_samples and X.shape[0] > max_samples:
        X = X[:max_samples]

    ref_df = pd.DataFrame(X)
    REFERENCE_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    ref_df.to_parquet(REFERENCE_FEATURES_PATH, index=False)

    print(
        f"[Drift] Reference baseline built with shape {ref_df.shape} "
        f"and saved to {REFERENCE_FEATURES_PATH}"
    )

    return ref_df


def _load_reference_features() -> pd.DataFrame:
    if REFERENCE_FEATURES_PATH.exists():
        return pd.read_parquet(REFERENCE_FEATURES_PATH)

    # Fallback: build from training data if not present
    return build_reference_baseline()


def generate_ecg_drift_report(
    current_features: pd.DataFrame,
    output_html: Path | str = "docs/ecg_drift_report.html",
) -> None:
    """
    Generate an Evidently drift report comparing:
    - Reference ECG feature distribution (built from training)
    - Current ECG feature batch (e.g., last N API requests)

    Args:
        current_features: DataFrame of features in the same schema as training features.
        output_html: Path to save the HTML drift report.
    """

    reference_df = _load_reference_features()
    output_path = Path(output_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = Report(
        metrics=[
            DataDriftPreset(),
        ]
    )

    report.run(reference_data=reference_df, current_data=current_features)
    report.save_html(str(output_path))

    print(f"[Drift] ECG drift report saved to {output_path}")


def compute_single_ecg_drift_score(
    signal_array: np.ndarray,
) -> float:
    """
    Compute a lightweight drift score for a single ECG signal relative to baseline.

    This function:
    - Extracts features using the same logic as the training pipeline
    - Compares them with the reference baseline distribution
    - Returns the share of features that are flagged as drifting

    NOTE: This is intentionally simple and used mainly for monitoring.
    """

    from src.pipeline.train import extract_features_from_signal

    reference_df = _load_reference_features()

    # Build a one-row DataFrame for the incoming ECG
    features = extract_features_from_signal(signal_array)
    current_df = pd.DataFrame([features], columns=reference_df.columns)

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=current_df)
    result = report.as_dict()

    # Extract a simple score: number of drifting features / total
    try:
        drifted_features = result["metrics"][0]["result"]["number_of_drifted_columns"]
        total_features = result["metrics"][0]["result"]["number_of_columns"]
        if total_features == 0:
            return 0.0
        return drifted_features / float(total_features)
    except Exception:
        return 0.0


def start_evidently_drift_dashboard(port: int = 7000, host: str = "0.0.0.0"):
    """
    Start an Evidently dashboard server for ECG drift monitoring.

    This creates a FastAPI server that:
    - Loads reference baseline from training data
    - Accepts current ECG feature batches via API
    - Generates and serves Evidently drift reports in real-time

    Usage:
        python -m src.monitoring.drift
        # Then visit http://localhost:7000
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
        import uvicorn
    except ImportError as e:
        print(f"Error: Missing required dependencies for dashboard server: {e}")
        print("Install with: pip install fastapi uvicorn sniffio")
        return

    app = FastAPI(title="HEARTSIGHT ECG Drift Dashboard")

    @app.get("/", response_class=HTMLResponse)
    def get_drift_dashboard():
        """Generate and return Evidently drift dashboard HTML for ECG features."""
        try:
            # Load reference baseline
            reference_df = _load_reference_features()

            # For demo: use a sample of reference as "current" (in production, this would come from API requests)
            # In a real setup, you'd collect recent ECG features from your API/inference pipeline
            current_df = reference_df.sample(
                min(100, len(reference_df)), random_state=42
            )

            # Generate Evidently report
            report = Report(
                metrics=[
                    DataDriftPreset(),
                ]
            )
            report.run(reference_data=reference_df, current_data=current_df)

            # Return HTML
            html_content = report.get_html()
            return HTMLResponse(content=html_content)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating drift dashboard: {e}"
            )

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "ecg-drift-dashboard",
            "reference_baseline_exists": REFERENCE_FEATURES_PATH.exists(),
        }

    @app.post("/update-current")
    def update_current_features(current_features: dict):
        """
        Update current features for drift monitoring (future enhancement).

        In production, this endpoint would accept feature batches from your
        inference pipeline and store them for comparison against the baseline.
        """
        # Placeholder for future implementation
        return {"message": "Feature update endpoint (to be implemented)"}

    print(f"Starting Evidently ECG Drift Dashboard on http://{host}:{port}")
    print(f"Visit http://localhost:{port} to view the dashboard")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        # Run dashboard server
        start_evidently_drift_dashboard()
    else:
        # Default: Example usage for offline drift report generation
        if not REFERENCE_FEATURES_PATH.exists():
            build_reference_baseline(max_samples=500)

        # For demonstration we reuse a small subset of reference as "current"
        ref = _load_reference_features()
        current = ref.sample(min(100, len(ref)), random_state=42)
        generate_ecg_drift_report(current_features=current)
