from fastapi import FastAPI

app = FastAPI(title="Federated ECGGuard API", version="1.0")

@app.get("/")
def root():
    return {"message": "Welcome to Federated ECGGuard API (This is just the Milestone 1 placeholder)"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/predict")
def predict():
    # mock response for now
    return {"message": "Mock prediction: Normal ECG signal"}