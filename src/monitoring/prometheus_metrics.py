from prometheus_client import start_http_server, Gauge
import random


def start_prometheus_metrics():
    """
    Exposes mock Prometheus metrics on port 9000.
    """
    gpu_usage = Gauge("gpu_usage_percent", "Mock GPU utilization")
    request_latency = Gauge("request_latency_seconds", "Mock latency per request")

    start_http_server(9000)
    print("Prometheus metrics available at http://localhost:9000/")

    while True:
        gpu_usage.set(random.uniform(10, 80))
        request_latency.set(random.uniform(0.05, 0.25))


if __name__ == "__main__":
    start_prometheus_metrics()
