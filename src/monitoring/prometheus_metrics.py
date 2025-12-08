"""
Prometheus metrics exporter for HEARTSIGHT MLOps pipeline.

Tracks:
- ECG Prediction metrics (latency, accuracy, distribution)
- Model performance (predictions per class)
- RAG/LLM metrics (latency, token usage, cost)
- Data drift indicators
- System health (requests, errors, uptime)

This module is safe to import from the API / RAG / model components.
The `start_prometheus_metrics` function is used by the dedicated
`metrics` service in docker-compose to expose metrics on port 9000.
"""

from __future__ import annotations

import time
from typing import Optional

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
)


# ---------------------------------------------------------
# ECG PREDICTION METRICS
# ---------------------------------------------------------

PREDICTION_REQUESTS_TOTAL = Counter(
    "prediction_requests_total",
    "Total number of prediction requests",
    ["status"],  # success, error, invalid_input
)

PREDICTION_LATENCY_SECONDS = Histogram(
    "prediction_latency_seconds",
    "Latency of ECG predictions (seconds)",
    ["stage"],  # model, rag, total
)

PREDICTION_CLASS_DISTRIBUTION = Counter(
    "prediction_class_distribution_total",
    "Distribution of predicted classes",
    ["predicted_class"],  # NORM, MI, STTC, CD, HYP
)

PREDICTION_CONFIDENCE = Histogram(
    "prediction_confidence",
    "Confidence scores of predictions",
    buckets=(0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99),
)

MODEL_PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds",
    "XGBoost model inference latency",
)

# ---------------------------------------------------------
# LLM & RAG METRICS
# ---------------------------------------------------------

LLM_LATENCY_SECONDS = Histogram(
    "llm_request_latency_seconds",
    "Latency of LLM calls (seconds)",
    ["endpoint"],
)

LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Approximate number of tokens processed by LLM calls",
    ["endpoint"],
)

LLM_COST_USD_TOTAL = Counter(
    "llm_cost_usd_total",
    "Approximate USD cost of LLM usage",
    ["endpoint"],
)

RAG_EXPLANATIONS_GENERATED = Counter(
    "rag_explanations_generated_total",
    "Total RAG explanations generated",
)

RAG_LATENCY_SECONDS = Histogram(
    "rag_latency_seconds",
    "Latency of RAG explanation generation",
)

CHAT_MESSAGES_TOTAL = Counter(
    "chat_messages_total",
    "Total chat messages processed",
)

# ---------------------------------------------------------
# DATA DRIFT & MODEL MONITORING
# ---------------------------------------------------------

MODEL_VERSION = Gauge(
    "model_version",
    "Current model version number",
)

DATA_DRIFT_SCORE = Gauge(
    "data_drift_score",
    "Evidently data drift score (0-1)",
)

GUARDRAIL_VIOLATIONS_TOTAL = Counter(
    "guardrail_violations_total",
    "Number of guardrail violations detected",
    ["endpoint", "stage", "rule"],
)

# ---------------------------------------------------------
# SYSTEM HEALTH METRICS
# ---------------------------------------------------------

API_REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

API_LATENCY_SECONDS = Histogram(
    "api_latency_seconds",
    "API request latency",
    ["endpoint"],
)

ERRORS_TOTAL = Counter(
    "errors_total",
    "Total errors by type",
    ["error_type"],
)

ACTIVE_PREDICTIONS = Gauge(
    "active_predictions_current",
    "Currently active predictions",
)

# ---------------------------------------------------------
# Recording Helpers
# ---------------------------------------------------------


def record_prediction(
    *,
    predicted_class: str,
    confidence: float,
    model_latency: float,
    rag_latency: float = 0.0,
    status: str = "success",
) -> None:
    """Record a complete prediction with all metrics."""
    try:
        PREDICTION_REQUESTS_TOTAL.labels(status=status).inc()
        PREDICTION_CLASS_DISTRIBUTION.labels(predicted_class=predicted_class).inc()
        PREDICTION_CONFIDENCE.observe(confidence)
        MODEL_PREDICTION_LATENCY.observe(model_latency)
        if rag_latency > 0:
            RAG_LATENCY_SECONDS.observe(rag_latency)
            PREDICTION_LATENCY_SECONDS.labels(stage="rag").observe(rag_latency)
        PREDICTION_LATENCY_SECONDS.labels(stage="model").observe(model_latency)
        PREDICTION_LATENCY_SECONDS.labels(stage="total").observe(
            model_latency + rag_latency
        )
    except Exception:
        pass


def record_llm_call(
    *, endpoint: str, latency_seconds: float, tokens: int, cost_usd: float = 0.0
) -> None:
    """Record a single LLM call in Prometheus metrics."""
    label = {"endpoint": endpoint}
    try:
        LLM_LATENCY_SECONDS.labels(**label).observe(latency_seconds)
        LLM_TOKENS_TOTAL.labels(**label).inc(max(tokens, 0))
        if cost_usd > 0:
            LLM_COST_USD_TOTAL.labels(**label).inc(cost_usd)
    except Exception:
        pass


def record_rag_explanation(latency_seconds: float) -> None:
    """Record RAG explanation generation."""
    try:
        RAG_EXPLANATIONS_GENERATED.inc()
        RAG_LATENCY_SECONDS.observe(latency_seconds)
    except Exception:
        pass


def record_chat_message() -> None:
    """Record a chat message."""
    try:
        CHAT_MESSAGES_TOTAL.inc()
    except Exception:
        pass


def record_guardrail_event(*, endpoint: str, stage: str, rule: str) -> None:
    """Increment guardrail violations counter."""
    try:
        GUARDRAIL_VIOLATIONS_TOTAL.labels(
            endpoint=endpoint, stage=stage, rule=rule
        ).inc()
    except Exception:
        pass


def set_model_version(version: int) -> None:
    """Set the current model version."""
    try:
        MODEL_VERSION.set(version)
    except Exception:
        pass


def set_data_drift_score(score: float) -> None:
    """Update data drift score from Evidently."""
    try:
        DATA_DRIFT_SCORE.set(score)
    except Exception:
        pass


def record_api_request(method: str, endpoint: str, status: int, latency: float) -> None:
    """Record API request metrics."""
    try:
        API_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
        API_LATENCY_SECONDS.labels(endpoint=endpoint).observe(latency)
    except Exception:
        pass


def record_error(error_type: str) -> None:
    """Record an error occurrence."""
    try:
        ERRORS_TOTAL.labels(error_type=error_type).inc()
    except Exception:
        pass


# ---------------------------------------------------------
# Exporter entrypoint (used by metrics container)
# ---------------------------------------------------------


def start_prometheus_metrics(port: int = 9000, sleep_interval: Optional[int] = 5):
    """
    Start the Prometheus HTTP server.

    This does not generate synthetic metrics; it only exposes whatever
    the application components record via the helpers above.

    When run as a standalone process (metrics container), it will:
    - start the HTTP server on the given port
    - sleep in a loop to keep the process alive
    """

    start_http_server(port)
    print(f"Prometheus metrics available at http://localhost:{port}/")

    # Keep the exporter process alive
    try:
        while True:
            time.sleep(sleep_interval or 5)
    except KeyboardInterrupt:
        print("Prometheus metrics exporter stopped.")


if __name__ == "__main__":
    start_prometheus_metrics()
