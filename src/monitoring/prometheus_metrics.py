"""
Prometheus metrics exporter for HEARTSIGHT.

In Phase 4 we track:
- LLM latency
- Token usage
- Approximate cost
- Guardrail violations (input/output)

This module is safe to import from the API / RAG / guardrails code.
The `start_prometheus_metrics` function is used by the dedicated
`metrics` service in docker-compose to expose metrics on port 9000.
"""

from __future__ import annotations

import time
from typing import Optional

from prometheus_client import (
    Counter,
    Histogram,
    start_http_server,
)


# ---------------------------------------------------------
# Metric Definitions
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

GUARDRAIL_VIOLATIONS_TOTAL = Counter(
    "guardrail_violations_total",
    "Number of guardrail violations detected",
    ["endpoint", "stage", "rule"],
)


# ---------------------------------------------------------
# Public recording helpers
# ---------------------------------------------------------


def observe_llm_call(
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
        # Metrics are best-effort; never break business logic
        pass


def record_guardrail_event(*, endpoint: str, stage: str, rule: str) -> None:
    """Increment guardrail violations counter from guardrails module."""

    try:
        GUARDRAIL_VIOLATIONS_TOTAL.labels(
            endpoint=endpoint, stage=stage, rule=rule
        ).inc()
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
