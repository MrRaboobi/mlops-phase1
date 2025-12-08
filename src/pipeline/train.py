import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report, accuracy_score
import xgboost as xgb
import mlflow
import mlflow.xgboost
import os

# --- CONFIGURATION ---
REPO_ROOT = os.getcwd()  # Assumes running from root of repo
DATA_PATH = os.path.join(REPO_ROOT, "data/raw")
META_FILE = os.path.join(DATA_PATH, "train_meta.csv")
SIGNAL_FILE = os.path.join(DATA_PATH, "train_signal.csv")

MLFLOW_EXPERIMENT_NAME = "Heartsight_Phase1_Baseline"

# Setup MLflow tracking URI (use file-based for local development)
os.makedirs("mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:./mlruns")


def extract_features_from_signal(signal_array):
    """
    Extract statistical features from ECG signal for tree-based models.
    Converts (TimeSteps, 12) array to a flat feature vector.

    Features extracted per channel:
    - Mean, std, min, max
    - Percentiles (25th, 50th, 75th)
    - Additional: range, variance
    """
    features = []

    # For each of the 12 channels
    for channel_idx in range(12):
        channel_data = signal_array[:, channel_idx]

        # Statistical features
        features.extend(
            [
                np.mean(channel_data),
                np.std(channel_data),
                np.min(channel_data),
                np.max(channel_data),
                np.percentile(channel_data, 25),
                np.percentile(channel_data, 50),  # median
                np.percentile(channel_data, 75),
                np.ptp(channel_data),  # range (peak-to-peak)
                np.var(channel_data),  # variance
            ]
        )

    return np.array(features)


def load_and_process_data():
    """
    1. Loads Metadata to get Labels.
    2. Loads Signal Data (Long format) and extracts features.
    3. Aligns them by ecg_id.
    """
    print("Loading Metadata...")
    if not os.path.exists(META_FILE) or not os.path.exists(SIGNAL_FILE):
        raise FileNotFoundError(
            f"Missing data files in {DATA_PATH}. "
            f"Ensure 'train_meta.csv' and 'train_signal.csv' exist. "
            f"Expected paths: {META_FILE}, {SIGNAL_FILE}"
        )

    meta_df = pd.read_csv(META_FILE)

    # 1. Prepare Targets (Labels)
    # The 5 diagnostic super-classes
    label_cols = ["NORM", "MI", "STTC", "CD", "HYP"]

    # Check if columns exist
    for col in label_cols:
        if col not in meta_df.columns:
            raise ValueError(f"Metadata is missing label column: {col}")

    # Convert One-Hot to Single Class Index (0-4)
    # We take the argmax. If a patient has multiple, we pick the highest priority/first one for simplicity in Phase 1.
    meta_df["target"] = meta_df[label_cols].idxmax(axis=1)

    # Encode 'NORM', 'MI' -> 0, 1, etc.
    le = LabelEncoder()
    meta_df["target_encoded"] = le.fit_transform(meta_df["target"])

    print("Loading Signal Data (This may take a moment)...")
    # Process data in chunks to avoid memory issues
    print("Processing signal data in chunks (memory-efficient)...")

    # Get unique ECG IDs from metadata
    meta_df = meta_df.sort_values("ecg_id")
    ecg_ids = meta_df["ecg_id"].values

    # Create a dictionary to store signals for each ECG ID
    ecg_signals = {}

    # Read CSV in chunks and group by ecg_id
    chunk_size = 50000
    print(f"Reading signal file in chunks of {chunk_size} rows...")
    for chunk_num, chunk in enumerate(pd.read_csv(SIGNAL_FILE, chunksize=chunk_size)):
        if chunk_num % 10 == 0:
            print(f"  Processed chunk {chunk_num}...")

        # Group by ecg_id within this chunk
        for ecg_id, group in chunk.groupby("ecg_id"):
            if ecg_id not in ecg_signals:
                ecg_signals[ecg_id] = []
            # Store the signal data (drop ecg_id column)
            ecg_signals[ecg_id].append(group.drop(columns=["ecg_id"]).values)

    # Combine chunks for each ECG ID
    print("Combining chunks for each ECG ID...")
    for ecg_id in ecg_signals:
        ecg_signals[ecg_id] = np.vstack(ecg_signals[ecg_id])

    # Extract aligned features
    print("Extracting features from signals...")
    aligned_features = []
    aligned_labels = []

    for ecg_id in ecg_ids:
        if ecg_id in ecg_signals:
            signal_array = ecg_signals[ecg_id]  # Shape: (TimeSteps, 12)

            # Extract features from signal
            features = extract_features_from_signal(signal_array)
            aligned_features.append(features)

            # Get label
            label = meta_df[meta_df["ecg_id"] == ecg_id]["target_encoded"].values[0]
            aligned_labels.append(label)
        else:
            print(f"Warning: ECG ID {ecg_id} not found in signal data, skipping...")

    X = np.array(
        aligned_features
    )  # Shape: (N, num_features) where num_features = 12 * 9 = 108
    y = np.array(aligned_labels)

    print(f"Data Loaded. Shape: {X.shape}, Labels: {y.shape}")
    print(f"Number of features per sample: {X.shape[1]}")
    print(f"Classes: {le.classes_}")

    return X, y, le.classes_


def build_model(num_classes, n_estimators=100, max_depth=6, learning_rate=0.1):
    """
    Build XGBoost classifier for multi-class classification.
    """
    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        objective="multi:softprob",  # Multi-class classification with probabilities
        num_class=num_classes,
        random_state=42,
        n_jobs=-1,  # Use all available CPUs
        eval_metric="mlogloss",
    )
    return model


def main():
    # 1. Setup MLflow (tracking URI already set at module level)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    try:
        X, y, class_names = load_and_process_data()
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Split Data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Training Config
    N_ESTIMATORS = 600
    MAX_DEPTH = 15
    LEARNING_RATE = 0.1

    with mlflow.start_run():
        print("Starting MLflow Run...")

        # Log Params
        mlflow.log_param("model_type", "XGBoost")
        mlflow.log_param("n_estimators", N_ESTIMATORS)
        mlflow.log_param("max_depth", MAX_DEPTH)
        mlflow.log_param("learning_rate", LEARNING_RATE)
        mlflow.log_param("data_source", "PTB-XL Reformatted")
        mlflow.log_param("feature_extraction", "statistical_features")

        # Build Model
        model = build_model(
            num_classes=len(class_names),
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            learning_rate=LEARNING_RATE,
        )

        print("Training XGBoost model...")
        # Train
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=True)

        # Evaluate
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        acc = accuracy_score(y_test, y_pred)
        print(f"Test Accuracy: {acc:.4f}")

        # Calculate F1 score (macro average for multi-class)
        f1 = f1_score(y_test, y_pred, average="macro")
        print(f"Test F1 Score (macro): {f1:.4f}")

        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=class_names))

        # Log Metrics
        mlflow.log_metric("test_accuracy", acc)
        mlflow.log_metric("f1_score", f1)

        # Log Artifacts
        # 1. The Model (Crucial for API) - Register in Model Registry
        signature = mlflow.models.infer_signature(X_test[:1], y_pred_proba[:1])
        mlflow.xgboost.log_model(
            model,
            "model",
            signature=signature,
            registered_model_name="heartsight_xgb_v1",
        )

        # 2. Class Names (Helper for API to map 0->NORM)
        class_names_path = "class_names.txt"
        with open(class_names_path, "w") as f:
            f.write("\n".join(class_names))
        mlflow.log_artifact(class_names_path)

        # Clean up temporary file
        if os.path.exists(class_names_path):
            os.remove(class_names_path)

        print(
            "\nRun Complete. Model registered as 'heartsight_xgb_v1' in MLflow Model Registry."
        )
        print(f"MLflow run URI: {mlflow.get_artifact_uri()}")


if __name__ == "__main__":
    main()
