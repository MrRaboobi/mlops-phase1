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
    report_result = report.run(reference_data=reference_data, current_data=current_data)

    # Try different methods to get HTML based on Evidently version
    html_content = None

    # Method 1: Try save_html (works in some versions)
    try:
        import os
        from pathlib import Path

        temp_dir = Path("/tmp")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / "evidently_dashboard.html"

        # Try save_html method
        if hasattr(report, "save_html"):
            report.save_html(str(temp_path))
            with open(temp_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            os.unlink(temp_path)
    except (AttributeError, Exception) as e:
        print(f"save_html method not available: {e}")

    # Method 2: Try get_html (works in some versions)
    if html_content is None:
        try:
            if hasattr(report, "get_html"):
                html_content = report.get_html()
        except (AttributeError, Exception) as e:
            print(f"get_html method not available: {e}")

    # Method 3: Try show() method
    if html_content is None:
        try:
            if hasattr(report, "show"):
                html_content = report.show()
        except (AttributeError, Exception) as e:
            print(f"show method not available: {e}")

    # Fallback: Generate simple HTML from report data
    if html_content is None:
        try:
            # Get report data for display (if available)
            _ = report_result.as_dict() if hasattr(report_result, "as_dict") else {}
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>HEARTSIGHT ECG Drift Dashboard</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    .info {{ background: #ecf0f1; padding: 20px; border-radius: 5px; }}
                    .metric {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #3498db; }}
                </style>
            </head>
            <body>
                <h1>❤️ HEARTSIGHT ECG Drift Dashboard</h1>
                <div class="info">
                    <h2>Data Drift Monitoring</h2>
                    <p><strong>Reference Data:</strong> {len(reference_data)} samples</p>
                    <p><strong>Current Data:</strong> {len(current_data)} samples</p>
                    <p><strong>Features Monitored:</strong> {', '.join(reference_data.columns.tolist()[:10])}</p>
                    <div class="metric">
                        <h3>Note:</h3>
                        <p>Full Evidently HTML report generation requires compatible Evidently version.</p>
                        <p>For full dashboard, use: <code>python -m src.monitoring.drift</code> to generate offline report.</p>
                        <p>Report will be saved to: <code>docs/ecg_drift_report.html</code></p>
                    </div>
                </div>
            </body>
            </html>
            """
        except Exception as e:
            html_content = f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"

    return HTMLResponse(content=html_content)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "evidently-dashboard"}


if __name__ == "__main__":
    import uvicorn

    print("Starting Evidently Dashboard on http://localhost:7000")
    uvicorn.run(app, host="0.0.0.0", port=7000)
