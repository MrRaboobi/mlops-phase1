# =========================
# Stage 1 — Builder
# =========================
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Enable persistent pip cache and install Python deps
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# =========================
# Stage 2 — Runtime
# =========================
FROM python:3.11-slim AS runtime
ENV APP_HOME=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR $APP_HOME

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY src/ src/
COPY scripts/ scripts/
COPY manage.py .

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create logs and data directories
RUN mkdir -p /app/logs /app/data /app/mlruns

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
