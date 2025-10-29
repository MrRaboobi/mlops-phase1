# src/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Milestone 1 Project",
    description="A production-ready repository skeleton for MLOps.",
    version="1.0.0",
)

@app.get("/")
def read_root():
    """A simple hello world endpoint."""
    return {"message": "Hello from the API"}

@app.get("/health")
def health_check():
    """Health check endpoint required for the Docker HEALTHCHECK instruction."""
    return {"status": "ok"}