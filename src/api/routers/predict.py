from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
from src.utils.model_loader import predict_ecg_signal

router = APIRouter()


class ECGSignalInput(BaseModel):
    """Input model for ECG signal prediction.

    The signal should be a 2D array where:
    - First dimension: time steps
    - Second dimension: 12 ECG channels (I, II, III, aVR, aVL, aVF, V1-V6)
    """

    signal: List[List[float]]  # Shape: (time_steps, 12)
    ecg_id: Optional[int] = None  # Optional patient ID for tracking


class ECGSimpleInput(BaseModel):
    """Simple input for backward compatibility (single value)."""

    signal_value: float


@router.post("/predict", tags=["Model"])
def predict_ecg(input_data: ECGSignalInput):
    """
    Predict ECG classification using the MLflow-registered model.

    Expected input format:
    {
        "signal": [[ch1_t1, ch2_t1, ..., ch12_t1],
                   [ch1_t2, ch2_t2, ..., ch12_t2],
                   ...],
        "ecg_id": 123  # optional
    }
    """
    try:
        # Convert to numpy array
        signal_array = np.array(input_data.signal)

        # Validate shape
        if len(signal_array.shape) != 2:
            raise HTTPException(
                status_code=400,
                detail=f"Signal must be 2D array (time_steps, 12). Got shape: {signal_array.shape}",
            )

        if signal_array.shape[1] != 12:
            raise HTTPException(
                status_code=400,
                detail=f"Signal must have 12 channels. Got {signal_array.shape[1]} channels",
            )

        # Get prediction
        prediction = predict_ecg_signal(signal_array)

        # Add metadata
        result = {
            "ecg_id": input_data.ecg_id,
            "signal_shape": list(signal_array.shape),
            **prediction,
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/predict/simple", tags=["Model"])
def predict_ecg_simple(input_data: ECGSimpleInput):
    """
    Simple prediction endpoint for backward compatibility.
    This is a mock endpoint - use /predict for real model inference.
    """
    result = "Normal" if input_data.signal_value < 0.5 else "Abnormal"
    return {
        "input_signal": input_data.signal_value,
        "prediction": result,
        "note": "This is a mock endpoint. Use /predict for real model inference.",
    }
