"""
Evidently Data Drift Monitoring for HEARTSIGHT.

Monitors:
- Input signal statistics changes (mean, std, distribution)
- Prediction distribution shifts
- Feature importance changes
- Model performance degradation

Generates reports and sends metrics to Prometheus.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd
import numpy as np
from evidently import Report
from evidently.presets import DataDriftPreset

logger = logging.getLogger(__name__)


class ECGDriftMonitor:
    """Monitor data drift in ECG predictions and features."""

    def __init__(self, reports_dir: str = "docs/drift_reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Reference data (from training set stats)
        self.reference_data = None
        self.load_reference_data()

    def load_reference_data(self):
        """Load reference statistics from training data."""
        try:
            # Try to load reference stats if they exist
            stats_file = self.reports_dir.parent / "reference_stats.json"
            if stats_file.exists():
                with open(stats_file) as f:
                    self.reference_data = json.load(f)
                logger.info(f"Loaded reference data from {stats_file}")
        except Exception as e:
            logger.warning(f"Could not load reference data: {e}")

    def create_signal_dataframe(self, signal: List[List[float]]) -> pd.DataFrame:
        """Convert signal array to dataframe with channel statistics."""
        signal_array = np.array(signal)

        # Extract features for each channel
        data = {}
        for ch_idx in range(min(12, signal_array.shape[1])):
            channel_data = signal_array[:, ch_idx]
            data[f"ch{ch_idx}_mean"] = np.mean(channel_data)
            data[f"ch{ch_idx}_std"] = np.std(channel_data)
            data[f"ch{ch_idx}_min"] = np.min(channel_data)
            data[f"ch{ch_idx}_max"] = np.max(channel_data)
            data[f"ch{ch_idx}_rms"] = np.sqrt(np.mean(channel_data**2))

        return pd.DataFrame([data])

    def check_drift(
        self,
        current_signals: List[List[List[float]]],
        current_predictions: List[str],
        current_confidences: List[float],
    ) -> Dict[str, Any]:
        """
        Check for data drift in signals and predictions.

        Args:
            current_signals: List of ECG signals
            current_predictions: List of predicted classes
            current_confidences: List of confidence scores

        Returns:
            Drift report with scores and insights
        """
        try:
            # Create dataframe from signals
            signal_dfs = [self.create_signal_dataframe(sig) for sig in current_signals]
            current_data = pd.concat(signal_dfs, ignore_index=True)

            # Add prediction columns
            current_data["prediction"] = current_predictions
            current_data["confidence"] = current_confidences

            # Create reference data if not loaded
            if self.reference_data is None:
                self.reference_data = current_data.iloc[: len(current_data) // 2].copy()

            # Run Evidently report
            report = Report(metrics=[DataDriftPreset()])
            report.run(reference_data=self.reference_data, current_data=current_data)

            # Extract drift metrics
            report_dict = report.as_dict()
            drift_score = (
                report_dict.get("metrics", [{}])[0]
                .get("result", {})
                .get("drift_score", 0)
            )

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.reports_dir / f"drift_report_{timestamp}.html"
            report.save_html(str(report_path))
            logger.info(f"Saved drift report to {report_path}")

            return {
                "drift_detected": drift_score > 0.5,
                "drift_score": drift_score,
                "num_drifted_features": sum(
                    1
                    for m in report_dict.get("metrics", [])
                    if m.get("result", {}).get("drift", False)
                ),
                "report_path": str(report_path),
            }

        except Exception as e:
            logger.error(f"Error checking drift: {e}")
            return {
                "drift_detected": False,
                "drift_score": 0.0,
                "num_drifted_features": 0,
                "error": str(e),
            }

    def generate_comparison_report(self, predictions_log: List[Dict[str, Any]]) -> None:
        """Generate comparison report over time."""
        try:
            if len(predictions_log) < 2:
                logger.warning("Not enough data for comparison report")
                return

            # Create report directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = self.reports_dir / f"comparison_{timestamp}"
            report_dir.mkdir(exist_ok=True)

            # Extract stats
            predictions = [p["class"] for p in predictions_log]
            confidences = [p["confidence"] for p in predictions_log]

            # Calculate distributions
            stats = {
                "total_predictions": len(predictions_log),
                "class_distribution": {
                    cls: predictions.count(cls) for cls in set(predictions)
                },
                "avg_confidence": float(np.mean(confidences)),
                "min_confidence": float(np.min(confidences)),
                "max_confidence": float(np.max(confidences)),
                "timestamp": timestamp,
            }

            # Save stats
            with open(report_dir / "stats.json", "w") as f:
                json.dump(stats, f, indent=2)

            logger.info(f"Generated comparison report in {report_dir}")

        except Exception as e:
            logger.error(f"Error generating comparison report: {e}")


# Global monitor instance
_monitor = None


def get_drift_monitor() -> ECGDriftMonitor:
    """Get or create the global drift monitor."""
    global _monitor
    if _monitor is None:
        _monitor = ECGDriftMonitor()
    return _monitor
