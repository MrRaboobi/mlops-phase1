# =========================
# Stage 1 — Builder
# =========================
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
