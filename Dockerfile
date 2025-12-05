# =========================
# Stage 1 — Builder
# =========================
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
# Upgrade pip and add generous timeouts/retries to reduce flaky network failures
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=120 --retries=10 -r requirements.txt

# =========================
# Stage 2 — Runtime
# =========================
FROM python:3.11-slim AS runtime
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Copy dependencies and source
COPY --from=builder /usr/local /usr/local
COPY src/ src/
COPY scripts/ scripts/

# Make healthcheck script executable
RUN chmod +x scripts/*.sh

# Create non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000
HEALTHCHECK CMD ["sh", "scripts/healthcheck.sh"]
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
