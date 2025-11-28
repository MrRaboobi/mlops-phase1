# Phase 1 Verification Guide

This guide helps you verify that Phase 1 is working correctly.

## Prerequisites

1. **Data Files**: Ensure you have the PTB-XL data files in `data/raw/`:
   - `train_meta.csv`
   - `train_signal.csv`

2. **Dependencies**: Install all required packages:
   ```powershell
   pip install -r requirements.txt
   ```

## Step 1: Run Training Pipeline

Execute the training script using the Windows management script:

```powershell
python manage.py train
```

**Expected Output:**
- Data loading messages
- Training progress (epochs)
- Test accuracy and F1 score
- Classification report
- MLflow registration confirmation

**Verification Points:**
- ✅ No errors during data loading
- ✅ Model trains successfully
- ✅ Metrics are logged to MLflow
- ✅ Model is registered in MLflow Model Registry

## Step 2: Verify MLflow Artifacts

After training, check that MLflow artifacts exist:

1. **Check MLflow Directory:**
   ```powershell
   dir mlruns
   ```
   You should see experiment directories.

2. **Verify Model Registry:**
   - Navigate to `mlruns/` folder
   - Look for `models/heartsight_cnn_v1/` directory
   - Verify model files exist

3. **Check Class Names Artifact:**
   - In the MLflow run directory, look for `artifacts/class_names.txt`
   - Should contain: NORM, MI, STTC, CD, HYP

## Step 3: Test API Model Loading

Start the FastAPI server:

```powershell
python manage.py dev
```

**Expected Output:**
- Server starts on `http://localhost:8000`
- Model loading attempt (may fail if no model exists yet - this is OK)
- API documentation available at `http://localhost:8000/docs`

## Step 4: Test Prediction Endpoint

Once the model is trained and the API is running, test the prediction endpoint:

**Using curl (PowerShell):**
```powershell
# Create a test JSON file
$testSignal = @{
    signal = @(
        @(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0),
        @(1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1, 12.1)
    )
    ecg_id = 123
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $testSignal -ContentType "application/json"
```

**Using Python:**
```python
import requests
import numpy as np

# Create a sample ECG signal (2 time steps, 12 channels)
signal = np.random.randn(100, 12).tolist()  # 100 time steps, 12 channels

response = requests.post(
    "http://localhost:8000/predict",
    json={"signal": signal, "ecg_id": 123}
)

print(response.json())
```

**Expected Response:**
```json
{
    "ecg_id": 123,
    "signal_shape": [100, 12],
    "predicted_class": "NORM",
    "confidence": 0.85,
    "probabilities": {
        "NORM": 0.85,
        "MI": 0.05,
        "STTC": 0.04,
        "CD": 0.03,
        "HYP": 0.03
    },
    "class_index": 0
}
```

## Step 5: Verify Evaluation Data

Check that the evaluation data file exists:

```powershell
Get-Content data/eval.jsonl
```

**Expected:**
- JSONL file with disease names and ground truth descriptions
- At least 5 entries (NORM, MI, STTC, CD, HYP)
- Used for prompt evaluation in Phase 3

## Troubleshooting

### Issue: "Model not found" error
**Solution:** Make sure you've run `python manage.py train` first and the model was successfully registered.

### Issue: "Missing data files" error
**Solution:** Verify that `data/raw/train_meta.csv` and `data/raw/train_signal.csv` exist.

### Issue: Import errors (tensorflow, mlflow)
**Solution:**
```powershell
pip install -r requirements.txt
```

### Issue: Model loads but predictions fail
**Solution:**
- Check that input signal shape is correct: (time_steps, 12)
- Verify the model was trained with the same input shape

## Success Criteria

Phase 1 is complete when:

- ✅ Training script runs without errors
- ✅ Model is registered in MLflow Model Registry
- ✅ MLflow artifacts (model, class_names.txt) exist
- ✅ API can load model from registry
- ✅ `/predict` endpoint returns valid predictions
- ✅ `data/eval.jsonl` exists with evaluation data

## Next Steps

Once Phase 1 is verified, proceed to:
- **Phase 2**: RAG Engine implementation
- **Phase 3**: Prompt Engineering & Evaluation
