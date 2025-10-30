#!/bin/sh
echo "Starting monitoring stack..."

# Start mock Prometheus metrics
python src/monitoring/prometheus_metrics.py &

# Generate Evidently drift report
python src/monitoring/drift_dashboard.py

# Log a dummy run in MLflow
python src/monitoring/mlflow_tracking.py

echo "Monitoring stack started (MLflow + Evidently + Prometheus)"
