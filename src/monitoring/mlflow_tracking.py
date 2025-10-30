import mlflow

def setup_mlflow():

    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("federated_ecg_experiment")

    with mlflow.start_run(run_name="mock_model_v1"):
        mlflow.log_param("model_type", "CNN-Mock")
        mlflow.log_metric("accuracy", 0.93)
        mlflow.set_tag("stage", "Milestone1")
        print("MLflow tracking initialized at ./mlruns")

if __name__ == "__main__":
    setup_mlflow()
