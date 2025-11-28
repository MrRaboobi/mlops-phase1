"""
Evidently Dashboard Server
Exposes Evidently dashboard on port 7000 for data drift monitoring.
"""

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="Evidently Data Drift Dashboard")

# Sample reference and current data (replace with actual data loading)
REFERENCE_DATA_PATH = os.getenv("REFERENCE_DATA_PATH", "data/raw/train_meta.csv")
CURRENT_DATA_PATH = os.getenv("CURRENT_DATA_PATH", "data/raw/test_meta.csv")


def load_data():
    """Load reference and current datasets for drift detection."""
    try:
        # Load metadata files (using available columns for drift detection)
        ref_df = pd.read_csv(REFERENCE_DATA_PATH, nrows=1000)  # Sample for demo
        curr_df = pd.read_csv(CURRENT_DATA_PATH, nrows=1000)  # Sample for demo

        # Select numeric columns for drift detection
        numeric_cols = ref_df.select_dtypes(
            include=["float64", "int64"]
        ).columns.tolist()
        if len(numeric_cols) == 0:
            # Fallback to sample data if no numeric columns
            ref_df = pd.DataFrame({"signal": [0.1, 0.2, 0.3, 0.4] * 250})
            curr_df = pd.DataFrame({"signal": [0.15, 0.25, 0.35, 0.45] * 250})
            numeric_cols = ["signal"]

        ref_data = ref_df[numeric_cols[:5]]  # Limit to 5 columns for performance
        curr_data = curr_df[numeric_cols[:5]]

        return ref_data, curr_data
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return sample data as fallback
        return (
            pd.DataFrame({"signal": [0.1, 0.2, 0.3, 0.4] * 250}),
            pd.DataFrame({"signal": [0.15, 0.25, 0.35, 0.45] * 250}),
        )


@app.get("/", response_class=HTMLResponse)
def get_drift_dashboard():
    """Generate and return Evidently drift dashboard HTML."""
    reference_data, current_data = load_data()

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_data, current_data=current_data)

    # Get HTML content
    html_content = report.get_html()

    return HTMLResponse(content=html_content)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "evidently-dashboard"}


if __name__ == "__main__":
    import uvicorn

    print("Starting Evidently Dashboard on http://localhost:7000")
    uvicorn.run(app, host="0.0.0.0", port=7000)
