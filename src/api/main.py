from fastapi import FastAPI
from src.api.routers import health, predict

app = FastAPI(
    title="Federated ECGGuard API",
    description="API documentation for the ECGGuard MLOps system. Provides endpoints for health monitoring and ECG signal predictions.",
    version="1.0.0",
)

# Include router modules
app.include_router(health.router)
app.include_router(predict.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Federated ECGGuard API"}


# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
